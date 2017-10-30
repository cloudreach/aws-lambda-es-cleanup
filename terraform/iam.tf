data "template_file" "policy" {
  template = "${file("${path.module}/files/es_policy.json")}"
}

resource "aws_iam_policy" "policy" {
  name        = "${var.prefix}es-cleanup"
  path        = "/"
  description = "Policy for es-cleanup Lambda function"
  policy      = "${data.template_file.policy.rendered}"
}

resource "aws_iam_role" "role" {
  name = "${var.prefix}es-cleanup"

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
  role       = "${aws_iam_role.role.name}"
  policy_arn = "${aws_iam_policy.policy.arn}"
}
