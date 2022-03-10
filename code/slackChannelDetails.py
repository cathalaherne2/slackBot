import json
import http.client
import boto3

from datadog_lambda.metric import lambda_metric
import os


token = os.environ['token']
client = boto3.client('dynamodb')
comprehend = boto3.client(service_name='comprehend')
lambda_client = boto3.client('lambda')

conn = http.client.HTTPSConnection("slack.com")
payload = ''
token = os.environ['token']
headers = {
  'Authorization': token
}

def lambda_handler(event, context):
    
    channel = event["channelID"]
    channelName = event["channelName"]
    conn.request("GET", "/api/conversations.history?channel={}".format(channel), payload, headers)

    res = conn.getresponse()
    data = res.read()
    datastructured = data.decode("utf-8")
    datastructured = json.loads(datastructured)
    
    #there was issues where the bot was not in a channel, therefore it cannot read messages. OK = True when bot is in channel, OK = False when not
    if datastructured["ok"]:
        for message in datastructured["messages"]:
            
            if "client_msg_id" in message:
                client_msg_id = "12345678"
                response = client.query(
                    TableName='slackChannelsMetadata',
                    KeyConditionExpression='id = :id',
                    ExpressionAttributeValues={
                        ':id': {'S': message["client_msg_id"]}
                    }
                )
                
                if not response["Items"]:
                    print("there was a new message")
                    SentimentScore = comprehend.detect_sentiment(Text=message["text"], LanguageCode='en')
                    print(SentimentScore["Sentiment"])
                    if "reply_count" not in message:
                        thread = False
                    if "reply_count" in message:
                        thread = True
                        
                    response = client.put_item(
                        TableName='slackChannelsMetadata',
                        Item={
                            'id':{'S': message["client_msg_id"]},
                            'channelID':{'S': channel},
                            'channelMessageName':{'S': channelName},
                            'message':{'S': message["text"]},
                            'user':{'S': message["user"]},
                            'timestamp':{'S': message["ts"]},
                            'Sentiment':{'S': SentimentScore["Sentiment"]},
                            'sentimentScorePositive':{'S': str(SentimentScore["SentimentScore"]["Positive"])},
                            'sentimentScoreNegative':{'S': str(SentimentScore["SentimentScore"]["Negative"])},
                            'sentimentScoreNeutral':{'S': str(SentimentScore["SentimentScore"]["Neutral"])},
                            'sentimentScoreMixed':{'S': str(SentimentScore["SentimentScore"]["Mixed"])},
                            'thread':{'BOOL': thread}
                        })
                    lambda_metric(
                        "slackmessages.message",             # Metric name
                        1,                                  # Metric value
                        tags=['sentiment:' + SentimentScore["Sentiment"], 'user:' + message["user"], 'channelName:' + channelName]  # Associated tags
                    )
                    print(message["client_msg_id"])
                    print(channel)
                    print(message["text"])
                    print(message["user"])
                    print(message["ts"])
                    sentimentScore = ""
                    print(sentimentScore)
                
                print(message)
                if "reply_count" not in message:
                    print("no thread")
                if "reply_count" in message:
                    print(" there is a thread")
                    lambda_payload = { "timestamp":message["thread_ts"],"channelID":channel, "channelName":channelName}
                    print(lambda_payload)
                    lambda_client.invoke(
                        FunctionName='slackThreadDetails', 
                        InvocationType='Event',
                        Payload= json.dumps(lambda_payload).encode('utf-8')
                        ) 
                        
    else:
        print("channel Name is {}".format(channelName))
        print(datastructured)
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }