import json
import json
import boto3
import uuid
import base64
import datetime
from boto3.dynamodb.conditions import Key, Attr
import botocore.vendored.requests as requests
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('users')
awk = boto3.client('rekognition','us-east-1')

def get_as_base64(url):

    return base64.b64encode(requests.get(url).content)
def lambda_handler(event, context):
    # TODO implement
    print(event)
    # #query the username's isValid field in dynamodb
    username = event["user"]
    url = event["body"]
    username = json.loads(username)
    username = username['username']
    # username = "shru"
    resp = table.scan(TableName="users",FilterExpression = Attr("username").eq(username))
    is_valid = resp['Items'][0]['is_valid']
    if is_valid:
        respose = "true"
    else:
        if url:
            b64 = get_as_base64(url)
            response = awk.detect_faces(
            Image={
                'Bytes':base64.decodestring(b64)
                },
            )
            
            if len(response["FaceDetails"])>=1:
                # return
                s3 = boto3.client('s3')
                bucket_name = 'cloudcomputingcolumbiaproject'
                key = username
                s3.put_object(Body=base64.decodestring(b64), Bucket = bucket_name, Key = key+".jpg",ContentType="images/jpeg")

                table.update_item(
                    Key={'username': username},
                    AttributeUpdates={
                        'is_valid': True,
                    },
                )
                response = "true"
            else:
                response = "false"
        
            
        else:
            response = "false"
    
    
    #return isvalid
    
    
    
    
    return {
        'statusCode': 200,
        'body': response
    }
