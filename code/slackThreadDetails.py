import json
import http.client
import boto3
from datadog_lambda.metric import lambda_metric
import os

client = boto3.client('dynamodb')
comprehend = boto3.client(service_name='comprehend')
token = os.environ['token']


conn = http.client.HTTPSConnection("slack.com")
payload = ''
headers = {
  'Authorization': token
}

def lambda_handler(event, context):
    
    timestamp = event["timestamp"]
    channelID = event["channelID"]
    channelName = event["channelName"]
    conn.request("GET", "/api/conversations.replies?ts={}&channel={}".format(timestamp, channelID), payload, headers)
    res = conn.getresponse()
    data = res.read()
    datastructured = data.decode("utf-8")
    datastructured = json.loads(datastructured)
    threadlength = datastructured["messages"][0]["reply_count"]
    print(threadlength)
    for message in range(0, threadlength):
        
        message = datastructured["messages"][message+1]
        print(message)
        if "client_msg_id" in message:
            
            response = client.query(
                    TableName='slackChannelsMetadata',
                    KeyConditionExpression='id = :id',
                    ExpressionAttributeValues={
                        ':id': {'S': message["client_msg_id"]}
                    }
                )
            print(response)
            if not response["Items"]:
                print("I got here")
                SentimentScore = comprehend.detect_sentiment(Text=message["text"], LanguageCode='en')
                print(type(SentimentScore))
                print(SentimentScore["Sentiment"])
                response = client.put_item(
                    TableName='slackChannelsMetadata',
                    Item={
                        'id':{'S': message["client_msg_id"]},
                        'channelID':{'S': channelID},
                        'channelMessageName':{'S': channelName},
                        'message':{'S': message["text"]},
                        'user':{'S': message["user"]},
                        'timestamp':{'S': message["ts"]},
                        'thread_timestamp':{'S': message["thread_ts"]},
                        'Sentiment':{'S': SentimentScore["Sentiment"]},
                        'sentimentScorePositive':{'S': str(SentimentScore["SentimentScore"]["Positive"])},
                        'sentimentScoreNegative':{'S': str(SentimentScore["SentimentScore"]["Negative"])},
                        'sentimentScoreNeutral':{'S': str(SentimentScore["SentimentScore"]["Neutral"])},
                        'sentimentScoreMixed':{'S': str(SentimentScore["SentimentScore"]["Mixed"])}
                    })
                    
                lambda_metric(
                    "slackmessages.message",             # Metric name
                    1,                                  # Metric value
                    tags=['sentiment:' + SentimentScore["Sentiment"], 'user:' + message["user"], 'channelName:' + channelName]  # Associated tags
                    )

                print(message["client_msg_id"])
                print(timestamp)
                print(message["text"])
                print(message["user"])
                print(message["ts"])
                sentimentScore = ""
                print(sentimentScore)

    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }

