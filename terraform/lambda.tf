data "archive_file" "es_cleanup_lambda" {
  type        = "zip"
  source_file = "${path.module}/../es-cleanup.py"
  output_path = "${path.module}/es-cleanup.zip"
}

locals {
  sg_ids = [element(concat(aws_security_group.lambda.*.id, [""]), 0)]
}

data "null_data_source" "lambda_file" {
  inputs = {
    filename = "${path.module}/es-cleanup.zip"
  }
}

resource "aws_lambda_function" "es_cleanup" {
  filename         = data.null_data_source.lambda_file.outputs.filename
  function_name    = "${var.prefix}es-cleanup${var.suffix}"
  description      = "${var.prefix}es-cleanup${var.suffix}"
  timeout          = 300
  runtime          = "python${var.python_version}"
  role             = aws_iam_role.role.arn
  handler          = "es-cleanup.lambda_handler"
  source_code_hash = data.archive_file.es_cleanup_lambda.output_base64sha256

  environment {
    variables = {
      es_endpoint           = var.es_endpoint
      index                 = var.index
      skip_index            = var.skip_index
      delete_after          = var.delete_after
      index_format          = var.index_format
      snapshot_enabled      = var.snapshot_enabled
      snapshot_repository   = var.snapshot_repository
      snapshot_delete_after = var.snapshot_delete_after
    }
  }

  tags = merge(
    var.tags,
    {
      "Scope" = "${var.prefix}lambda_function_to_elasticsearch${var.suffix}"
    },
  )

  # This will be a code block with empty lists if we don't create a securitygroup and the subnet_ids are empty.
  # When these lists are empty it will deploy the lambda without VPC support.
  vpc_config {
    subnet_ids         = var.subnet_ids
    security_group_ids = compact(concat(local.sg_ids, var.security_group_ids))
  }
}

