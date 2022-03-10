resource "aws_cloudwatch_event_rule" "eventBridgeInvokeRule" {
  name        = "eventBridgeInvokeRule"
  description = "this rule will invoke Lambda every 15 minutes to scan for any new messages/channels etc"
  schedule_expression = "cron(0/15 * * * ? *)"
}


