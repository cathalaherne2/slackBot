data "archive_file" "slackChannelUsers" {
  type        = "zip"
  source_file = "code/slackChannelUsers.py"
  output_path = "outputs/slackChannelUsers.zip"
}

resource "aws_lambda_function" "slackChannelUsers" {
  filename      = "outputs/slackChannelUsers.zip"
  function_name = "slackChannelUsers"
  role          = "${aws_iam_role.slackBotAssumyPolicy.arn}"
  memory_size   = "624"
  timeout       = "60"
  handler       = "datadog_lambda.handler.handler"
  layers        = ["arn:aws:lambda:eu-west-1:464622532012:layer:Datadog-Extension:17",
                   "arn:aws:lambda:eu-west-1:464622532012:layer:Datadog-Python39:50"]

  source_code_hash = "${data.archive_file.slackChannelUsers.output_base64sha256}"

  runtime = "python3.9"

  tags = {
    createdBy = "cathal"
    service = "slackChannelUsers"
  }

  environment {
    variables = {
      DD_LAMBDA_HANDLER = "slackChannelUsers.lambda_handler"
      DD_TRACE_ENABLED = "true"
      env = "prod"
      service = "slack"
      token = local.slack_creds.slacktoken
      DD_API_KEY = local.slack_creds.ddapikey
    }
  }
}


resource "aws_cloudwatch_event_target" "slackChannelUsers" {
  arn  = aws_lambda_function.slackChannelUsers.arn
  rule = aws_cloudwatch_event_rule.eventBridgeInvokeRule.id
}

resource "aws_lambda_permission" "slackChannelUsersPermission" {
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.slackChannelUsers.function_name
  principal     = "events.amazonaws.com"
  source_arn    = "${aws_cloudwatch_event_rule.eventBridgeInvokeRule.arn}"
}