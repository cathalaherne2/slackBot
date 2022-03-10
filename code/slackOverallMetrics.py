import json
import boto3
from datadog_lambda.metric import lambda_metric

client = boto3.client('dynamodb')


def lambda_handler(event, context):

    responses = client.scan(
        TableName='slackChannelsMetadata',
        FilterExpression="attribute_exists(channelName)",
    )
    

    lambda_metric(
        "slackmessages.channels",   # Metric name
        responses["Count"]
    )
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
