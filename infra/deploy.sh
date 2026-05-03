#!/usr/bin/env bash
# deploy.sh – Build, push to ECR, and deploy to ECS Fargate
# Usage: AWS_ACCOUNT_ID=123456789 AWS_REGION=us-east-1 ./infra/deploy.sh [image-tag]
set -euo pipefail

AWS_ACCOUNT_ID="${AWS_ACCOUNT_ID:?AWS_ACCOUNT_ID is required}"
AWS_REGION="${AWS_REGION:-us-east-1}"
REPO_NAME="multimodel-ai-platform"
CLUSTER="multimodel-ai-cluster"
SERVICE="multimodel-ai-service"
IMAGE_TAG="${1:-$(git rev-parse --short HEAD 2>/dev/null || echo latest)}"
ECR_URI="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${REPO_NAME}"

echo "==> Logging in to ECR"
aws ecr get-login-password --region "$AWS_REGION" \
  | docker login --username AWS --password-stdin "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"

echo "==> Building image: ${ECR_URI}:${IMAGE_TAG}"
docker build -t "${REPO_NAME}:${IMAGE_TAG}" .
docker tag "${REPO_NAME}:${IMAGE_TAG}" "${ECR_URI}:${IMAGE_TAG}"
docker tag "${REPO_NAME}:${IMAGE_TAG}" "${ECR_URI}:latest"

echo "==> Pushing to ECR"
docker push "${ECR_URI}:${IMAGE_TAG}"
docker push "${ECR_URI}:latest"

echo "==> Rendering task definition"
export IMAGE_TAG AWS_ACCOUNT_ID AWS_REGION
TASK_DEF=$(envsubst < infra/ecs/task-definition.json)

echo "==> Registering task definition"
TASK_DEF_ARN=$(echo "$TASK_DEF" \
  | aws ecs register-task-definition \
      --cli-input-json file:///dev/stdin \
      --region "$AWS_REGION" \
      --query 'taskDefinition.taskDefinitionArn' \
      --output text)

echo "==> Task definition registered: ${TASK_DEF_ARN}"

echo "==> Updating ECS service: ${CLUSTER}/${SERVICE}"
aws ecs update-service \
  --cluster "$CLUSTER" \
  --service "$SERVICE" \
  --task-definition "$TASK_DEF_ARN" \
  --force-new-deployment \
  --region "$AWS_REGION"

echo "==> Waiting for service stability..."
aws ecs wait services-stable \
  --cluster "$CLUSTER" \
  --services "$SERVICE" \
  --region "$AWS_REGION"

echo "==> Deploy complete: ${ECR_URI}:${IMAGE_TAG}"
