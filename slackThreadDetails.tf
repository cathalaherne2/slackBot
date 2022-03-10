data "archive_file" "slackThreadDetails" {
  type        = "zip"
  source_file = "code/slackThreadDetails.py"
  output_path = "outputs/slackThreadDetails.zip"
}

resource "aws_lambda_function" "slackThreadDetails" {
  filename      = "outputs/slackThreadDetails.zip"
  function_name = "slackThreadDetails"
  role          = "${aws_iam_role.slackBotAssumyPolicy.arn}"
  memory_size   = "624"
  timeout       = "60"
  handler       = "datadog_lambda.handler.handler"
  layers        = ["arn:aws:lambda:eu-west-1:464622532012:layer:Datadog-Extension:17",
                   "arn:aws:lambda:eu-west-1:464622532012:layer:Datadog-Python39:50"]

  source_code_hash = "${data.archive_file.slackThreadDetails.output_base64sha256}"

  runtime = "python3.9"

  tags = {
    createdBy = "cathal"
    service = "slackThreadDetails"
  }

  environment {
    variables = {
      DD_LAMBDA_HANDLER = "slackThreadDetails.lambda_handler"
      DD_TRACE_ENABLED = "true"
      env = "prod"
      service = "slack"
      token = local.slack_creds.slacktoken
      DD_API_KEY = local.slack_creds.ddapikey
    }
  }
}
