import json
import http.client
import boto3
import os

client = boto3.client('dynamodb')


conn = http.client.HTTPSConnection("slack.com")
token = os.environ['token']
payload = ''
headers = {
  'Authorization': token
}

connstring = "/api/users.list"

def lambda_handler(event, context):
    conn.request("GET", connstring, payload, headers)
    
    res = conn.getresponse()
    data = res.read()
    datastructured = data.decode("utf-8")
    datastructuredJson = json.loads(datastructured)
    
    # imitating if a cursor was returned
    #datastructuredJson["response_metadata"]["next_cursor"] = "dXNlcjpVMEc5V0ZYTlo="
    print(datastructuredJson)
    
    
    
    
    while True:
        for member in datastructuredJson["members"]:
            callAPI(member)
        
        if datastructuredJson["response_metadata"]["next_cursor"]:
            curser = datastructuredJson["response_metadata"]["next_cursor"].replace("=", "%3D")
            apstring = connstring + "&" + curser
            conn.request("GET", apstring, payload, headers)
            print(apstring)
            res = conn.getresponse()
            data = res.read()
            datastructured = data.decode("utf-8")
            try:
                datastructuredJson = json.loads(datastructured)
            except ValueError:  # includes simplejson.decoder.JSONDecodeError
                print('Decoding JSON has failed, curser was' + datastructuredJson["response_metadata"]["next_cursor"])
                break
        else:
            break




def callAPI(member):
    
    response = client.query(
            TableName='slackChannelsMetadata',
            KeyConditionExpression='id = :id',
            ExpressionAttributeValues={
                ':id': {'S': member["id"]}
            }
        )

    print(response)
    if not response["Items"]:
        response = client.put_item(
            TableName='slackChannelsMetadata',
            Item={
                'id':{'S': member["id"]},
                'name':{'S': member["name"]},
                'team_id':{'S': member["team_id"]},
                'timestamp':{'S': str(member["updated"])}
            })
    