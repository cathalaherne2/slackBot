import json
import http.client
import boto3

client = boto3.client('dynamodb')

def lambda_handler(event, context):
    print(event)
    
    
    responses = client.scan(
                    TableName='slackChannelsMetadata',
                    FilterExpression='channelpairing = :channelpairing',
                    ExpressionAttributeValues={
                        ':channelpairing': {'S': event["channelID"]}
                    }
                )
                
    for response in responses["Items"]:
        
        print(response)
        
        response = client.delete_item(
            TableName='slackChannelsMetadata',
            Key={
                'id': {
                    'S': response["id"]["S"]
                    
                }   
            }
        )
    
    responses = client.scan(
                    TableName='slackChannelsMetadata',
                    FilterExpression='channelID = :channelID',
                    ExpressionAttributeValues={
                        ':channelID': {'S': event["channelID"]}
                    }
                )
    for response in responses["Items"]:
        
        print(response)
        
        response = client.delete_item(
            TableName='slackChannelsMetadata',
            Key={
                'id': {
                    'S': response["id"]["S"]
                    
                }
            }
        )
        
    responses = client.scan(
                    TableName='slackChannelsMetadata',
                    FilterExpression='id = :id',
                    ExpressionAttributeValues={
                        ':id': {'S': event["channelID"]}
                    }
                )
    for response in responses["Items"]:
        
        print(response)
        
        response = client.delete_item(
            TableName='slackChannelsMetadata',
            Key={
                'id': {
                    'S': response["id"]["S"]
                    
                }
                    
            }
        )
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
