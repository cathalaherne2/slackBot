import json
import http.client
import boto3
import uuid
import time
import os

token = os.environ['token']
conn = http.client.HTTPSConnection("slack.com")
payload = ''
headers = {
  'Authorization': token
}
client = boto3.client('dynamodb')


def lambda_handler(event, context):
    
    channel = event["channelID"]
    conn.request("GET", "/api/conversations.members?channel={}".format(channel), payload, headers)
    res = conn.getresponse()
    data = res.read()
    datastructured = data.decode("utf-8")
    datastructured = json.loads(datastructured)
    print(datastructured)
    for member in datastructured["members"]:
        
        
        ts = time.time()
        id = channel + member
        print("ID is: " + id)
        print("channel ID is :" + channel)

        print(id)
        
        response = client.query(
            TableName='slackChannelsMetadata',
            KeyConditionExpression='id = :id',
            ExpressionAttributeValues={
                ':id': {'S': id}
            }
        )
        print(response)
        if not response["Items"]:
            response = client.put_item(
                TableName='slackChannelsMetadata',
                Item={
                    'id':{'S': id},
                    'memberPairing':{'S': member},
                    'channelpairing':{'S': channel}
    
                    })
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
