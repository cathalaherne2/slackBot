data "archive_file" "slackChannelDetails" {
  type        = "zip"
  source_file = "code/slackChannelDetails.py"
  output_path = "outputs/slackChannelDetails.zip"
}

resource "aws_lambda_function" "slackChannelDetails" {
  filename      = "outputs/slackChannelDetails.zip"
  function_name = "slackChannelDetails"
  role          = "${aws_iam_role.slackBotAssumyPolicy.arn}"
  memory_size   = "624"
  timeout       = "60"
  handler       = "datadog_lambda.handler.handler"
  layers        = ["arn:aws:lambda:eu-west-1:464622532012:layer:Datadog-Extension:17",
                   "arn:aws:lambda:eu-west-1:464622532012:layer:Datadog-Python39:50"]

  source_code_hash = "${data.archive_file.slackChannelDetails.output_base64sha256}"

  runtime = "python3.9"

  tags = {
    createdBy = "cathal"
    service = "slackChannelDetails"
  }

  environment {
    variables = {
      DD_LAMBDA_HANDLER = "slackChannelDetails.lambda_handler"
      DD_TRACE_ENABLED = "true"
      env = "prod"
      service = "slack"
      token = local.slack_creds.slacktoken
      DD_API_KEY = local.slack_creds.ddapikey
    }
  }
}
