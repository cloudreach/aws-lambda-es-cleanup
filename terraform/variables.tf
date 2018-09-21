variable "prefix" {
  default = ""
}

variable "suffix" {
  default = ""
}

variable "schedule" {
  default = "cron(0 3 * * ? *)"
}

variable "sns_alert" {
  description = "SNS ARN to pusblish any alert"
  default     = ""
}

variable "es_endpoint" {}

variable "index" {
  description = "Index/indices to process comma separated, with all every index will be processed except '.kibana'"
  default     = "all"
}

variable "delete_after" {
  description = "Numbers of days to preserve"
  default     = 15
}

variable "index_format" {
  description = "Combined with 'index' varible is used to evaluate the index age"
  default     = "%Y.%m.%d"
}

variable "python_version" {
  default = "2.7"
}

variable "subnet_ids" {
  description = "Subnet IDs you want to deploy the lambda in. Only fill this in if you want to deploy your Lambda function inside a VPC."
  type        = "list"
  default     = []
}

variable "security_group_ids" {
  description = "Addiational Security Ids To add."
  type        = "list"
  default     = []
}

variable "tags" {
  description = "Tags to apply"
  default = {
    Name = "es-cleanup"
  }
}
