
# Slackbot built by Cathal



### What is the problem we are trying to solve:

right now, Sales engineers have no active method for monitoring their slack channels. This means that as an engineer/manager, there are no statistics regarding how active is a channel, is it several engineers in a channel who are active? are the message becoming more active over time?

Using this bot, these are the exact questions we are answering.

### How does this solve the problem:

using the slack API, we are currently pulling information on the following:

List all public/private slack channels which currently exist
List all users in the environment which currently exist

for each slack channel, list every message that was sent.

gather context on these messages such as sentiment + the name of the user and the channel, and store this info.

for each message that was sent, read all threads contained inside, gathering the same info as a standard message.


___

In the event that a channel is archieved, this channels data will automatically be cleared out, to ensure we are not storing data we no longer need.



### How does this work:

Every 15 minutes, a cloudwatch rule triggers, calling 3 lambda functions.

after this, we then call the appropriate downstream functions, such as if there is a message with a thread -> call thread function etc.

we store metadata on these messages in DynamoDB, and so this solution is completely serverless.

finally, we log metrics we wish to track in Datadog, so that we can track number of messages per channel, number of channels that exist etc.







