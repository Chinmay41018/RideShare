import json
# from PIL import Image
import botocore.vendored.requests as requests
import boto3
import base64
dynamodb = boto3.client('dynamodb')

awk = boto3.client('rekognition','us-east-1')

def get_as_base64(url):
    return base64.b64encode(requests.get(url).content)
    
def lambda_handler(event, context):
    print(event)
    phone_number = event['request']['userAttributes']['phone_number']
    family_name = event['request']['userAttributes']['family_name']
    given_name = event['request']['userAttributes']['given_name']
    url = event['request']['userAttributes']['picture']
    username = event['userName']
    # url = "https://claustraum.com/wp-content/uploads/2018/12/Attitude-status-images-for-Facebook-profile-pic-1024x1024.png"
    # url = "https://dxs1x0sxlq03u.cloudfront.net/sites/default/files/article-image/eminence-organics-acne-face-mapping.jpg"
    b64 = get_as_base64(url)
    response = awk.detect_faces(
            Image={
                'Bytes':base64.decodestring(b64)
                },
        )
    s3 = boto3.client('s3')
    bucket_name = 'cloudcomputingcolumbiaproject'
    key = username
    s3.put_object(Body=base64.decodestring(b64), Bucket = bucket_name, Key = key+".jpg",ContentType="images/jpeg")
    if len(response["FaceDetails"])>=1:
        face = True
    else:
        face = False
    d = {
      	'username': {'S': username}, 
        'last_name': {'S': family_name},
        'first_name': {'S': given_name},
        'number': {'S' : phone_number}, 
        'is_valid': {'BOOL': face}
         }    
    response = dynamodb.put_item(
    TableName='users',
    Item=d)
    return event