data "archive_file" "slackOverallMetrics" {
  type        = "zip"
  source_file = "code/slackOverallMetrics.py"
  output_path = "outputs/slackOverallMetrics.zip"
}

resource "aws_lambda_function" "slackOverallMetrics" {
  filename      = "outputs/slackOverallMetrics.zip"
  function_name = "slackOverallMetrics"
  role          = "${aws_iam_role.slackBotAssumyPolicy.arn}"
  memory_size   = "624"
  timeout       = "60"
  handler       = "datadog_lambda.handler.handler"
  layers        = ["arn:aws:lambda:eu-west-1:464622532012:layer:Datadog-Extension:17",
                   "arn:aws:lambda:eu-west-1:464622532012:layer:Datadog-Python39:50"]

  source_code_hash = "${data.archive_file.slackOverallMetrics.output_base64sha256}"

  runtime = "python3.9"

  tags = {
    createdBy = "cathal"
    service = "slackOverallMetrics"
  }

  environment {
    variables = {
      DD_LAMBDA_HANDLER = "slackOverallMetrics.lambda_handler"
      DD_TRACE_ENABLED = "true"
      env = "prod"
      service = "slack"
      token = local.slack_creds.slacktoken
      DD_API_KEY = local.slack_creds.ddapikey
    }
  }
}

resource "aws_cloudwatch_event_target" "slackOverallMetrics" {
  arn  = aws_lambda_function.slackOverallMetrics.arn
  rule = aws_cloudwatch_event_rule.eventBridgeInvokeRule.id
}

resource "aws_lambda_permission" "slackOverallMetricsPermission" {
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.slackOverallMetrics.function_name
  principal     = "events.amazonaws.com"
  source_arn    = "${aws_cloudwatch_event_rule.eventBridgeInvokeRule.arn}"
}