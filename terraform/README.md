# terraform module

This directory contains terraform 0.9 module for deleting old Elasticsearch
indices.

Particularly it creates:

1. Lambda function that does the deletion
2. IAM role and policy that allows access to ES
3. Cloudwatch event rule that triggers the lambda function on a schedule
4. (Only when your Lambda is deployed inside a VPC) Securitygroup for Lambda function

## Module Input Variables


| Variable Name | Example Value | Description | Default Value | Required |
| --- | --- | --- | --- |  --- |
| es_endpoint | search-es-demo-zveqnhnhjqm5flntemgmx5iuya.eu-west-1.es.amazonaws.com  | AWS ES fqdn | `None` | True |
| index |  `logstash,cwl` | Index/indices to process comma separated, with `all` every index will be processed except `.kibana` | `all` | False |
| index_format  | `%Y.%m.%d` | Combined with `index` varible is used to evaluate the index age | `%Y.%m.%d` |  False |
| delete_after | `7` | Numbers of days to preserve | `15` |  False |
| sns_alert | `arn:aws:sns:eu-west-1:123456789012:sns-alert` | SNS ARN to publish any alert | | False |
| prefix | `public-` | A prefix for the resource names, this helps create multiple instances of this stack for different environments | | False |

### Required

* `es_endpoint` - Elasticsearch endpoint.

### Optional

* `index` - Prefix of the index names. e.g. `logstash` if your indices look
like `logstash-2017.10.30`.
* `delete_after` - How many days old to keep. Default 7
* `index_format` - Variable section of the index names, if
you indices look like `logstash-2017.10.30`. Default `%Y.%m.%d`
* `sns_alert` - SNS topic ARN to send failure alerts to.
* `prefix` - A prefix for the resource names, this helps create multiple
instances of this stack for different environments and regions.
* `schedule` - Schedule expression for running the cleanup function.
* `python_version` - Python version to be used. Defaults to 2.7
Default is once a day at 03:00 GMT.
See: http://docs.aws.amazon.com/AmazonCloudWatch/latest/events/ScheduledEvents.html
* `subnet_ids` - Subnet IDs you want to deploy the lambda in. Only fill this in if you want to deploy your Lambda function inside a VPC.
## Usage

```
module "public_es_cleanup" {
  source = "github.com/cloudreach/aws-lambda-es-cleanup.git//terraform"

  prefix       = "public_es_"
  es_endpoint  = "test-es-XXXXXXX.eu-central-1.es.amazonaws.com"
  delete_after = 60
}


module "vpc_es_cleanup" {
  source = "github.com/cloudreach/aws-lambda-es-cleanup.git//terraform"

  prefix       = "vpc_es_"
  es_endpoint  = "vpc-gc-demo-vpc-gloo5rzcdhyiykwdlots2hdjla.eu-central-1.es.amazonaws.com"
  index        = "all"
  delete_after = 30
  subnet_ids     = ["subnet-d8660da2"]
}
```
