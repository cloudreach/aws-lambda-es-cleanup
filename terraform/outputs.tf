output "iam_role_arn" {
  description = "AWS IAM ARN"
  value       = aws_iam_role.role.arn
}

output "lambda_arn" {
  description = "AWS Lambda ARN"
  value       = aws_lambda_function.es_cleanup.arn
}

output "cloudwatch_event_arn" {
  description = "AWS Cloudwatch Event ARN"
  value       = aws_cloudwatch_event_rule.schedule.arn
}
