data "archive_file" "slackAsyncRetiredChannels" {
  type        = "zip"
  source_file = "code/slackAsyncRetiredChannels.py"
  output_path = "outputs/slackAsyncRetiredChannels.zip"
}

resource "aws_lambda_function" "slackAsyncRetiredChannels" {
  filename      = "outputs/slackAsyncRetiredChannels.zip"
  function_name = "slackAsyncRetiredChannels"
  role          = "${aws_iam_role.slackBotAssumyPolicy.arn}"
  memory_size   = "624"
  timeout       = "60"
  handler       = "datadog_lambda.handler.handler"
  layers        = ["arn:aws:lambda:eu-west-1:464622532012:layer:Datadog-Extension:17",
                   "arn:aws:lambda:eu-west-1:464622532012:layer:Datadog-Python39:50"]

  source_code_hash = "${data.archive_file.slackAsyncRetiredChannels.output_base64sha256}"

  runtime = "python3.9"

  tags = {
    createdBy = "cathal"
    service = "slackAsyncRetiredChannels"
  }

  environment {
    variables = {
      DD_LAMBDA_HANDLER = "slackAsyncRetiredChannels.lambda_handler"
      DD_TRACE_ENABLED = "true"
      env = "prod"
      service = "slack"
      token = local.slack_creds.slacktoken
      DD_API_KEY = local.slack_creds.ddapikey
    }
  }
}
