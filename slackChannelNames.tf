data "aws_kms_secrets" "creds" {
    secret {
      name    = "slack"
      payload = file("${path.module}/slack-creds.yml.encrypted")
    }
  }

locals {
  slack_creds = yamldecode(data.aws_kms_secrets.creds.plaintext["slack"])
}

data "archive_file" "slackChannelNames" {
  type        = "zip"
  source_file = "code/slackChannelNames.py"
  output_path = "outputs/slackChannelNames.zip"
}

resource "aws_lambda_function" "slackChannelNames" {
  filename      = "outputs/slackChannelNames.zip"
  function_name = "slackChannelNames"
  role          = "${aws_iam_role.slackBotAssumyPolicy.arn}"
  memory_size   = "624"
  timeout       = "60"
  handler       = "datadog_lambda.handler.handler"
  layers        = ["arn:aws:lambda:eu-west-1:464622532012:layer:Datadog-Extension:17",
                   "arn:aws:lambda:eu-west-1:464622532012:layer:Datadog-Python39:50"]

  source_code_hash = "${data.archive_file.slackChannelNames.output_base64sha256}"

  runtime = "python3.9"

  tags = {
    createdBy = "cathal"
    service = "slackChannelNames"
  }

  environment {
    variables = {
      DD_LAMBDA_HANDLER = "slackChannelNames.lambda_handler"
      DD_TRACE_ENABLED = "true"
      env = "prod"
      service = "slack"
      token = local.slack_creds.slacktoken
      DD_API_KEY = local.slack_creds.ddapikey
    }
  }
}


resource "aws_cloudwatch_event_target" "slackChannelNames" {
  arn  = aws_lambda_function.slackChannelNames.arn
  rule = aws_cloudwatch_event_rule.eventBridgeInvokeRule.id
}


resource "aws_lambda_permission" "slackChannelNamesPermission" {
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.slackChannelNames.function_name
  principal     = "events.amazonaws.com"
  source_arn    = "${aws_cloudwatch_event_rule.eventBridgeInvokeRule.arn}"
}
