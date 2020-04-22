# Module Input Variables

<!-- BEGINNING OF PRE-COMMIT-TERRAFORM DOCS HOOK -->
## Providers

| Name | Version |
|------|---------|
| archive | n/a |
| aws | n/a |
| null | n/a |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:-----:|
| delete\_after | Numbers of days to preserve | `number` | `15` | no |
| es\_endpoint | AWS ES FQDN e.g. search-es-demo-xxxxxxxxxx.eu-west-1.es.amazonaws.com | `string` | n/a | yes |
| index | Index/indices to process using regex, except the one matching `skip_index` regex | `string` | `".*"` | no |
| index\_format | Combined with 'index' varible is used to evaluate the index age | `string` | `"%Y.%m.%d"` | no |
| prefix | A prefix for the resource names, this helps create multiple instances of this stack for different environments | `string` | `""` | no |
| python\_version | Lambda Python version to be used | `string` | `"3.6"` | no |
| schedule | Cloudwatch Cron Schedule expression for running the cleanup function | `string` | `"cron(0 3 * * ? *)"` | no |
| security\_group\_ids | Addiational Security Ids To add. | `list(string)` | `[]` | no |
| skip\_index | Index/indices to skip | `string` | `".kibana*"` | no |
| subnet\_ids | Subnet IDs you want to deploy the lambda in. Only fill this in if you want to deploy your Lambda function inside a VPC. | `list(string)` | `[]` | no |
| suffix | A suffix for the resource names, this helps create multiple instances of this stack for different environments | `string` | `""` | no |
| tags | Tags to apply | `map` | <pre>{<br>  "Name": "es-cleanup"<br>}</pre> | no |
| timeout | Maximum lambda execution time | `number` | `300` | no |

## Outputs

| Name | Description |
|------|-------------|
| cloudwatch\_event\_arn | AWS Cloudwatch Event ARN |
| iam\_role\_arn | AWS IAM ARN |
| lambda\_arn | AWS Lambda ARN |

<!-- END OF PRE-COMMIT-TERRAFORM DOCS HOOK -->


## pre-commit hook

this repo is using pre-commit hook to know more [click here](https://github.com/antonbabenko/pre-commit-terraform)
to manually trigger use this command

```
pre-commit install
pre-commit run --all-files
```


## Example

```
terraform {
  required_version = ">= 0.12"
}

provider "aws" {
  region = "eu-west-1"
}

module "public_es_cleanup" {
  source       = "github.com/cloudreach/aws-lambda-es-cleanup.git//terraform?ref=v0.14"

  prefix       = "public_es_"
  es_endpoint  = "test-es-XXXXXXX.eu-central-1.es.amazonaws.com"
  delete_after = 365
}


module "vpc_es_cleanup" {
  source             = "github.com/cloudreach/aws-lambda-es-cleanup.git//terraform?ref=v0.14"

  prefix             = "vpc_es_"
  es_endpoint        = "vpc-gc-demo-vpc-gloo5rzcdhyiykwdlots2hdjla.eu-central-1.es.amazonaws.com"
  index              = "all"
  delete_after       = 30
  subnet_ids         = ["subnet-d8660da2"]
  security_group_ids = ["sg-02dd3aa6da1b5"]
}
```


### Issue
In order order to use new module version you must have `terraform-provider-aws` greated than `~> 2.7` and use Terraform `~> 0.12`
