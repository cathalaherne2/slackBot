import json
import http.client
import boto3
import os


client = boto3.client('dynamodb')
lambda_client = boto3.client('lambda')
token = os.environ['token']


def lambda_handler(event, context):
    conn = http.client.HTTPSConnection("slack.com")
    payload = ''
    headers = {
      'Authorization': token
    }
    conn.request("GET", "/api/conversations.list?types=public_channel%2Cprivate_channel", payload, headers)

    res = conn.getresponse()
    data = res.read()
    datastructured = data.decode("utf-8")
    datastructured = json.loads(datastructured)
    
    print("the following is the response from Slack")

    print(datastructured)
    

    for channel in datastructured["channels"]:
        lambda_payload = { "channelID":channel["id"],"channelName":channel["name"]
            
        }
        
        print(lambda_payload)
        response = client.query(
                TableName='slackChannelsMetadata',
                KeyConditionExpression='id = :id',
                ExpressionAttributeValues={
                    ':id': {'S': channel["id"]}
                })
                
        if channel["is_archived"]:
                
            if response["Items"]:
                print("I am in the Database but am archived {}".format(channel["id"]))
                lambda_client.invoke(
                    FunctionName='slackAsyncRetiredChannels', 
                    InvocationType='Event',
                    Payload= json.dumps(lambda_payload).encode('utf-8')
                    )
            else:
                print("I am archived but am not in the Database")
        
        else:
            if not response["Items"]:
                print(channel["id"] + " was not in the database")
                
                response = client.put_item(
                    TableName='slackChannelsMetadata',
                    Item={
                        'id':{'S': channel["id"]},
                        'channelName':{'S': channel["name"]},
                        'timestamp':{'S': str(channel["created"])}
                    })
            if "Items" in response:
                if response["Items"]:
                    print("I am not archived and I am in the Database")
        
            lambda_client.invoke(
                FunctionName='slackChannelUserPairings', 
                InvocationType='Event',
                Payload= json.dumps(lambda_payload).encode('utf-8')
                )
            
            print("Invoking Lambda to read messages from channel {}".format(channel["id"]))
            lambda_client.invoke(
                FunctionName='slackChannelDetails', 
                InvocationType='Event',
                Payload= json.dumps(lambda_payload).encode('utf-8')
                )
    
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }