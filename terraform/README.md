# terraform module

This directory contains terraform 0.9 module for deleting old Elasticsearch
indices.

Particularly it creates:

1. Lambda function that does the deletion
2. IAM role and policy that allows access to ES
3. Cloudwatch event rule that triggers the lambda function on a schedule

## Module Input Variables

### Required

* `es_endpoint` - Elasticsearch endpoint.
* `index` - Prefix of the index names. e.g. `logstash` if your indices look
like `logstash-2017.10.30`.
* `delete_after` - How many days old to keep.
* `index_format` - Variable section of the index names. e.g. `%Y.%m.%d` if
you indices look like `logstash-2017.10.30`.

### Optional

* `sns_alert` - SNS topic ARN to send failure alerts to.
* `prefix` - A prefix for the resource names, this helps create multiple
instances of this stack for different environments and regions.
* `schedule` - Schedule expression for running the cleanup function.
Default is once a day at 03:00 GMT.
See: http://docs.aws.amazon.com/AmazonCloudWatch/latest/events/ScheduledEvents.html

## Usage

```
module "es_cleanup" {
  source = "github.com/cloudreach/aws-lambda-es-cleanup.git//terraform"

  prefix       = "test-eu-central-1-"
  es_endpoint  = "test-es-XXXXXXX.eu-central-1.es.amazonaws.com"
  sns_alert    = "arn:aws:sns:eu-central-1:123456789012:alertme"
  index        = "logstash"
  delete_after = 60
  index_format = "%Y.%m.%d"
}
```
