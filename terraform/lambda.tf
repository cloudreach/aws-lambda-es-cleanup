data "archive_file" "es_cleanup_lambda" {
  type        = "zip"
  source_file = "${path.module}/../es-cleanup.py"
  output_path = "${path.module}/es-cleanup.zip"
}

resource "aws_lambda_function" "es_cleanup_vpc" {
  count            = "${length(var.subnet_ids) > 0 ? 1 : 0}"
  filename         = "${path.module}/es-cleanup.zip"
  function_name    = "${var.prefix}es-cleanup"
  description      = "${var.prefix}es-cleanup"
  timeout          = 300
  runtime          = "python${var.python_version}"
  role             = "${aws_iam_role.role.arn}"
  handler          = "es-cleanup.lambda_handler"
  source_code_hash = "${data.archive_file.es_cleanup_lambda.output_base64sha256}"

  environment {
    variables = {
      es_endpoint  = "${var.es_endpoint}"
      index        = "${var.index}"
      delete_after = "${var.delete_after}"
      index_format = "${var.index_format}"
      sns_alert    = "${var.sns_alert}"
    }
  }

  tags = "${merge(
            var.tags,
            map("Scope", "${var.prefix}lambda_function_to_elasticsearch"),
            )}"
  # This will be a code block with empty lists if we don't create a securitygroup and the subnet_ids are empty.
  # When these lists are empty it will deploy the lambda without VPC support.
  vpc_config {
    subnet_ids         = ["${var.subnet_ids}"]
    security_group_ids = ["${aws_security_group.lambda.*.id}"]
  }
}

resource "aws_lambda_function" "es_cleanup" {
  count            = "${length(var.subnet_ids) == 0 ? 1 : 0}"
  filename         = "${path.module}/es-cleanup.zip"
  function_name    = "${var.prefix}es-cleanup"
  description      = "${var.prefix}es-cleanup"
  timeout          = 300
  runtime          = "python${var.python_version}"
  role             = "${aws_iam_role.role.arn}"
  handler          = "es-cleanup.lambda_handler"
  source_code_hash = "${data.archive_file.es_cleanup_lambda.output_base64sha256}"

  vpc_config {
    subnet_ids         = ["${split(",", var.subnet_ids)}"]
    security_group_ids = ["${split(",", var.sg_ids)}"]
  }

  environment {
    variables = {
      es_endpoint  = "${var.es_endpoint}"
      index        = "${var.index}"
      delete_after = "${var.delete_after}"
      index_format = "${var.index_format}"
      sns_alert    = "${var.sns_alert}"
    }
  }

  tags = "${merge(
            var.tags,
            map("Scope", "${var.prefix}lambda_function_to_elasticsearch"),
            )}"
}
