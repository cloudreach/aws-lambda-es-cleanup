data "aws_subnet" "selected" {
  count = "${length(var.subnet_ids) > 0 ? 1 : 0}"
  id    = "${var.subnet_ids[0]}"
}

resource "aws_security_group" "lambda" {
  count       = "${length(var.subnet_ids) > 0 ? 1 : 0}"
  name        = "lambda_cleanup_to_elasticsearch_${var.prefix}"
  description = "Lambda sg for cleanup function to elasticsearch"
  vpc_id      = "${data.aws_subnet.selected.vpc_id}"

  tags {
    Name        = "lambda_function_to_elasticsearch_${var.prefix}"
    Environment = "${var.prefix}"
  }
}

resource "aws_security_group_rule" "lambda_to_es" {
  count                    = "${length(var.subnet_ids) > 0 ? 1 : 0}"
  type                     = "egress"
  from_port                = 443
  to_port                  = 443
  protocol                 = "tcp"
  source_security_group_id = "${var.elasticsearch_sg_id}"

  security_group_id = "${aws_security_group.lambda.id}"
}

resource "aws_security_group_rule" "es_from_lambda" {
  count                    = "${length(var.subnet_ids) > 0 ? 1 : 0}"
  type                     = "ingress"
  from_port                = 443
  to_port                  = 443
  protocol                 = "tcp"
  source_security_group_id = "${aws_security_group.lambda.id}"

  security_group_id = "${var.elasticsearch_sg_id}"
}
