variable "prefix" {  default = "" }

variable "schedule" { default = "cron(0 3 * * ? *)" }

variable "sns_alert" { default = "" }

variable "es_endpoint" {}

variable "index" {}

variable "delete_after" {}

variable "index_format" {}

variable "python_version" { default = "2.7" }
