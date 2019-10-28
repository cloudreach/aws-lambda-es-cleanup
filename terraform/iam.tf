data "aws_region" "current" {
}

data "aws_caller_identity" "current" {
}

data "aws_iam_policy_document" "policy" {
  statement {
    sid    = "LambdaLogCreation"
    effect = "Allow"
    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents",
    ]
    resources = [
      "arn:aws:logs:${data.aws_region.current.name}:*:log-group:/aws/lambda/${var.prefix}es-cleanup${var.suffix}",
      "arn:aws:logs:${data.aws_region.current.name}:*:log-group:/aws/lambda/${var.prefix}es-cleanup${var.suffix}:*",
    ]
  }

  statement {
    sid    = "LambdaVPCconfig"
    effect = "Allow"
    actions = [
      "ec2:CreateNetworkInterface",
      "ec2:DescribeNetworkInterfaces",
      "ec2:DeleteNetworkInterface",
    ]
    resources = ["*"]
  }

  statement {
    sid    = "ESPermission"
    effect = "Allow"
    actions = [
      "es:*",
    ]
    resources = [
      "arn:aws:es:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:domain/*",
    ]
  }
}

resource "aws_iam_policy" "policy" {
  name        = "${var.prefix}es-cleanup${var.suffix}"
  path        = "/"
  description = "Policy for ${var.prefix}es-cleanup${var.suffix} Lambda function"
  policy      = data.aws_iam_policy_document.policy.json
}

resource "aws_iam_role" "role" {
  name = "${var.prefix}es-cleanup${var.suffix}"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF

}

resource "aws_iam_role_policy_attachment" "policy_attachment" {
  role       = aws_iam_role.role.name
  policy_arn = aws_iam_policy.policy.arn
}

resource "aws_iam_role_policy_attachment" "policy_attachment_vpc" {
  count      = length(var.subnet_ids) > 0 ? 1 : 0
  role       = aws_iam_role.role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"
}

