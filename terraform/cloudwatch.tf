resource "aws_cloudwatch_event_rule" "schedule" {
  name                = "${var.prefix}es-cleanup-execution-schedule${var.suffix}"
  description         = "${var.prefix}es-cleanup execution schedule${var.suffix}"
  schedule_expression = "${var.schedule}"
}

resource "aws_cloudwatch_event_target" "es_cleanup" {
  target_id = "${var.prefix}lambda-es-cleanup${var.suffix}"
  rule      = "${aws_cloudwatch_event_rule.schedule.name}"
  arn       = "${aws_lambda_function.es_cleanup.arn}"
}

resource "aws_lambda_permission" "allow_cloudwatch" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = "${aws_lambda_function.es_cleanup.arn}"
  principal     = "events.amazonaws.com"
  source_arn    = "${aws_cloudwatch_event_rule.schedule.arn}"
}
