variable "prefix" {
  default = ""
}

variable "schedule" {
  default = "cron(0 3 * * ? *)"
}

variable "sns_alert" {
  default = ""
}

variable "es_endpoint" {}

variable "index" {}

variable "delete_after" {}

variable "index_format" {}

variable "python_version" {
  default = "2.7"
}

variable "subnet_ids" {
  description = "Subnet IDs you want to deploy the lambda in. Only fill this in if you want to deploy your Lambda function inside a VPC."
  type        = "list"
  default     = []
}

variable "elasticsearch_sg_id" {
  description = "Security group ID of the AWS elasticsearch service. Only fill this in if you deploy Lambda function inside a VPC."
  default     = ""
}
