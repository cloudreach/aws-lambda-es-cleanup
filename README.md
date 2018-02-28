# AWS Lambda Elasticsearch Index Cleanup

## Overview
This AWS Lambda function allows you to delete the old Elasticsearch indexes using SigV4Auth authentication. You configure the AWS Elasticsearch Access Policy authorizing the Lambda Role or the AWS Account number instead of using the IP address whitelist.

## Getting Started
### How To install

Clone your repository

```bash
$ git clone git@github.com:cloudreach/aws-lambda-es-cleanup.git
$ cd aws-lambda-es-cleanup/
```

Configure in a proper way the IAM policy inside `json_file/es_policy.json` and `json_file/trust_policy.json`

Create the IAM Role

```bash
$ aws iam create-role --role-name es-cleanup-lambda \
	--assume-role-policy-document file://json_file/trust_policy.json

```

```bash
$ aws iam put-role-policy --role-name es-cleanup-lambda \
    --policy-name es_cleanup \
    --policy-document file://json_file/es_policy.json
```

Create your Lambda package

```bash
$ zip es-cleanup-lambda.zip es-cleanup.py
```



### Lambda deployment
Using awscli you can create your AWS function and set the proper IAM role with the right Account ID

```bash
$ export AWS_DEFAULT_REGION=eu-west-1
$ ESENDPOINT="search-es-demo-zveqnhnhjqm5flntemgmx5iuya.eu-west-1.es.amazonaws.com" #ES endpoint

$ aws lambda create-function \
	--function-name es-cleanup-lambda \
	--environment Variables={es_endpoint=$ESENDPOINT} \
	--zip-file fileb://es-cleanup-lambda.zip \
	--description "Elastichsearch Index Cleanup" \
	--role arn:aws:iam::123456789012:role/es-cleanup-lambda \
	--handler es-cleanup.lambda_handler \
	--runtime python2.7 \
	--timeout 180
```

If you want to send variables and not to use environment
```bash
$ export AWS_DEFAULT_REGION=eu-west-1

$ aws lambda create-function \
	--function-name es-cleanup-lambda \
	--zip-file fileb://es-cleanup-lambda.zip \
	--description "Elastichsearch Index Cleanup" \
	--role arn:aws:iam::123456789012:role/es-cleanup-lambda \
	--handler es-cleanup.lambda_handler \
	--runtime python2.7 \
	--timeout 180
```

### Lambda invoke with parameters
is it possible to override the default behaviour passing specific payload

```bash
$ aws lambda invoke
 --function-name es-cleanup-lambda \
 outfile --payload \
 '{"es_endpoint":"search-es-demo-zveqnhnhjqm5flntemgmx5iuya.eu-west-1.es.amazonaws.com"}'
```

Create your AWS Cloudwatch rule:

```bash
$ aws events put-rule \
	--name my-scheduled-rule \
	--schedule-expression 'cron(0 1 * * ? *)'


$ aws lambda add-permission \
	--function-name es-cleanup-lambda \
	--statement-id my-scheduled-event \
	--action 'lambda:InvokeFunction' \
	--principal events.amazonaws.com \
	--source-arn arn:aws:events:eu-west-1:123456789012:rule/my-scheduled-rule    


$ aws events put-targets \
	--rule my-scheduled-rule \
	--targets file://json_file/cloudwatch-target.json
```

### Lambda configuration and OS parameters

Using AWS environment variable you can easily modify the behaviour of the Lambda function

| Variable Name | Example Value | Description | Default Value | Required |
| --- | --- | --- | --- |  --- |
| es_endpoint | search-es-demo-zveqnhnhjqm5flntemgmx5iuya.eu-west-1.es.amazonaws.com  | AWS ES fqdn | `None` | True |
| index |  `logstash,cwl` | Index/indices to process comma separated, with `all` every index will be processed except `.kibana` | `all` | False |
| index_format  | `%Y.%m.%d` | Combined with `index` varible is used to evaluate the index age | `%Y.%m.%d` |  False |
| delete_after | `7` | Numbers of days to preserve | `15` |  False |
| sns_alert | `arn:aws:sns:eu-west-1:123456789012:sns-alert` | SNS ARN to publish any alert | | False |

## Serverless Framework

Editing the file `serverless.yml`, you can deploy your function in AWS using [Serverless Framework](https://serverless.com/framework/docs/providers/aws/cli-reference/)

```bash
$ git clone git@github.com:cloudreach/aws-lambda-es-cleanup.git
$ cd aws-lambda-es-cleanup/
$ serverless deploy
Serverless: Creating Stack...
Serverless: Checking Stack create progress...
.....
Serverless: Stack create finished...
Serverless: Packaging service...
Serverless: Uploading CloudFormation file to S3...
Serverless: Uploading function .zip files to S3...
Serverless: Uploading service .zip file to S3 (7.13 KB)...
Serverless: Updating Stack...
Serverless: Checking Stack update progress...
......................
Serverless: Stack update finished...
Service Information
service: es-cleanup-lambda
stage: prod
region: eu-west-1
api keys:
  None
endpoints:
  None
functions:
  es-cleanup-lambda: es-cleanup-lambda-prod-es-cleanup-lambda
```

### Terraform deployment

This lambda function can be also build using terraform followings this [README](terraform/README.md).

## How to Contribute

We encourage contribution to our projects, please see our [CONTRIBUTING](CONTRIBUTING.md) guide for details.


## License

**aws-lambda-es-cleanup** is licensed under the [Apache Software License 2.0](LICENSE.md).

## Thanks

Keep It Cloudy ([@CloudreachKIC](https://twitter.com/cloudreachkic))
