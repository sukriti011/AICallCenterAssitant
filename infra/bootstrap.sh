#!/usr/bin/env bash
# bootstrap.sh – One-time AWS resource creation for the platform
# Usage: AWS_ACCOUNT_ID=123456789 AWS_REGION=us-east-1 S3_BUCKET_NAME=my-bucket ./infra/bootstrap.sh
set -euo pipefail

AWS_ACCOUNT_ID="${AWS_ACCOUNT_ID:?AWS_ACCOUNT_ID is required}"
AWS_REGION="${AWS_REGION:-us-east-1}"
S3_BUCKET_NAME="${S3_BUCKET_NAME:?S3_BUCKET_NAME is required}"
REPO_NAME="multimodel-ai-platform"
CLUSTER="multimodel-ai-cluster"

echo "==> Creating ECR repository"
aws ecr create-repository \
  --repository-name "$REPO_NAME" \
  --region "$AWS_REGION" \
  --image-scanning-configuration scanOnPush=true \
  --output text --query 'repository.repositoryUri' || echo "(already exists)"

echo "==> Creating S3 bucket: ${S3_BUCKET_NAME}"
if [ "$AWS_REGION" = "us-east-1" ]; then
  aws s3api create-bucket --bucket "$S3_BUCKET_NAME" --region "$AWS_REGION" || echo "(already exists)"
else
  aws s3api create-bucket --bucket "$S3_BUCKET_NAME" --region "$AWS_REGION" \
    --create-bucket-configuration LocationConstraint="$AWS_REGION" || echo "(already exists)"
fi

echo "==> Enabling S3 bucket versioning"
aws s3api put-bucket-versioning \
  --bucket "$S3_BUCKET_NAME" \
  --versioning-configuration Status=Enabled

echo "==> Creating CloudWatch log group"
aws logs create-log-group \
  --log-group-name /ecs/multimodel-ai-platform \
  --region "$AWS_REGION" || echo "(already exists)"

echo "==> Creating ECS cluster"
aws ecs create-cluster \
  --cluster-name "$CLUSTER" \
  --capacity-providers FARGATE FARGATE_SPOT \
  --region "$AWS_REGION" \
  --output text --query 'cluster.clusterArn' || echo "(already exists)"

echo "==> Creating IAM execution role"
EXEC_ROLE_ARN=$(aws iam create-role \
  --role-name multimodel-ai-ecs-execution-role \
  --assume-role-policy-document '{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Principal":{"Service":"ecs-tasks.amazonaws.com"},"Action":"sts:AssumeRole"}]}' \
  --query 'Role.Arn' --output text 2>/dev/null || \
  aws iam get-role --role-name multimodel-ai-ecs-execution-role --query 'Role.Arn' --output text)

aws iam attach-role-policy \
  --role-name multimodel-ai-ecs-execution-role \
  --policy-arn arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy 2>/dev/null || true

export AWS_ACCOUNT_ID AWS_REGION S3_BUCKET_NAME
EXEC_POLICY=$(envsubst < infra/iam/execution-role-policy.json)
aws iam put-role-policy \
  --role-name multimodel-ai-ecs-execution-role \
  --policy-name multimodel-ai-execution-policy \
  --policy-document "$EXEC_POLICY"

echo "==> Creating IAM task role"
aws iam create-role \
  --role-name multimodel-ai-ecs-task-role \
  --assume-role-policy-document '{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Principal":{"Service":"ecs-tasks.amazonaws.com"},"Action":"sts:AssumeRole"}]}' \
  --output text --query 'Role.Arn' 2>/dev/null || echo "(already exists)"

TASK_POLICY=$(envsubst < infra/iam/task-role-policy.json)
aws iam put-role-policy \
  --role-name multimodel-ai-ecs-task-role \
  --policy-name multimodel-ai-task-policy \
  --policy-document "$TASK_POLICY"

echo ""
echo "==> Bootstrap complete!"
echo "    ECR:     ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${REPO_NAME}"
echo "    S3:      s3://${S3_BUCKET_NAME}"
echo "    Cluster: ${CLUSTER}"
echo ""
echo "Next: store secrets in Secrets Manager, create VPC/ALB/ECS service, then run ./infra/deploy.sh"
