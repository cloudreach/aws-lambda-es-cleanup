variable "prefix" {
  description = "A prefix for the resource names, this helps create multiple instances of this stack for different environments"
  default     = ""
  type        = string
}

variable "suffix" {
  description = "A suffix for the resource names, this helps create multiple instances of this stack for different environments"
  default     = ""
  type        = string
}

variable "schedule" {
  description = "Cloudwatch Cron Schedule expression for running the cleanup function"
  default     = "cron(0 3 * * ? *)"
  type        = string
}

variable "timeout" {
  description = "Maximum lambda execution time"
  default     = 300
  type        = number
}

variable "es_endpoint" {
  description = "AWS ES FQDN e.g. search-es-demo-xxxxxxxxxx.eu-west-1.es.amazonaws.com"
  type        = string
}

variable "index" {
  description = "Index/indices to process using regex, except the one matching `skip_index` regex"
  default     = ".*"
  type        = string
}

variable "skip_index" {
  description = "Index/indices to skip"
  default     = ".kibana*"
  type        = string
}

variable "delete_after" {
  description = "Numbers of days to preserve"
  default     = 15
  type        = number
}

variable "index_format" {
  description = "Combined with 'index' varible is used to evaluate the index age"
  default     = "%Y.%m.%d"
  type        = string
}

variable "python_version" {
  description = "Lambda Python version to be used"
  default     = "3.6"
  type        = string
}

variable "subnet_ids" {
  description = "Subnet IDs you want to deploy the lambda in. Only fill this in if you want to deploy your Lambda function inside a VPC."
  type        = list(string)
  default     = []
}

variable "security_group_ids" {
  description = "Addiational Security Ids To add."
  type        = list(string)
  default     = []
}

variable "tags" {
  description = "Tags to apply"
  default = {
    Name = "es-cleanup"
  }
}
