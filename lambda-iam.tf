resource "aws_iam_role_policy" "slackBotPermissions" {
  name = "slackBotPermissions"
  role = "${aws_iam_role.slackBotAssumyPolicy.id}"

  policy = "${file("iam/lambda-policy.json")}"
}

resource "aws_iam_role" "slackBotAssumyPolicy" {
  name = "slackBotAssumyPolicy"
  assume_role_policy = "${file("iam/lambda-assumepolicy.json")}"
}