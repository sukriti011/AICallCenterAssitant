# ECS Service Definition (reference – create via AWS Console or CLI)
#
# aws ecs create-service \
#   --cluster multimodel-ai-cluster \
#   --service-name multimodel-ai-service \
#   --task-definition multimodel-ai-platform \
#   --desired-count 2 \
#   --launch-type FARGATE \
#   --network-configuration "awsvpcConfiguration={subnets=[subnet-XXXX,subnet-YYYY],securityGroups=[sg-XXXX],assignPublicIp=DISABLED}" \
#   --load-balancers "targetGroupArn=arn:aws:elasticloadbalancing:...,containerName=api,containerPort=8000" \
#   --deployment-configuration "minimumHealthyPercent=100,maximumPercent=200" \
#   --health-check-grace-period-seconds 30 \
#   --region us-east-1

# ---- Recommended ALB + ECS Architecture ----
#
#   Internet
#      │
#   [ALB]  (port 443 HTTPS → port 80 redirect)
#      │
#   [Target Group]  (port 8000, health check: GET /health, 200 OK)
#      │
#   [ECS Fargate Tasks]  (2 tasks, awsvpc networking, private subnets)
#      │
#   [S3]  (document storage, accessed via task IAM role)
#   [Secrets Manager]  (API keys, injected as env vars at task start)
#   [CloudWatch Logs]  (/ecs/multimodel-ai-platform)
#
# Security Groups:
#   ALB SG:  inbound 443 from 0.0.0.0/0
#   Task SG: inbound 8000 from ALB SG only
