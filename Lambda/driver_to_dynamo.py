import json
import boto3
import uuid
# https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html#DynamoDB.Client.put_item
def lambda_handler(event, context):
    # TODO implement
    username = event["userId"]
    print(username)
    from_address = event["currentIntent"]["slots"]["FromLocation"]
    to_address = event["currentIntent"]["slots"]["ToLocation"]
    start_date = event["currentIntent"]["slots"]["startDate"]
    start_time = event["currentIntent"]["slots"]["startTime"]
    num_riders = event["currentIntent"]["slots"]["numRiders"]
    city = event["currentIntent"]["slots"]["city"]
    trip_id = str(uuid.uuid1())
    d = {
      		'from': {'S': from_address}, 
          'to': {'S': to_address},
          'start_date': {'S': str(start_date)},
          'start_time': {'S' : start_time}, 
          'num_riders': {'N': num_riders} ,
          'trip_id' : {'S': trip_id},
          'city': {'S' : city},
          'username': {'S':username},
          'route' : {'L' : [
            					{'M':   {'location' : {'S' : from_address}, 'user_id' : {'S' : trip_id}, 'user_role' : {'S' : 'driver'}, 'type' : {'S' : 'start' }}   }, 
          						{'M':   {'location' : {'S' : to_address}, 'user_id' : {'S' : trip_id}, 'user_role' : {'S' : 'driver'}, 'type' : {'S' : 'end' }}   }
          				]}
                    
        
         }
  
         
    
    dynamodb = boto3.client('dynamodb')
    
    response = dynamodb.put_item(
    TableName='trips',
    Item=d)

    lex_response = { 
        "dialogAction": 
        { 
        "type":"Close", 
        "fulfillmentState":'Fulfilled', 
        "message":{ 
            "contentType":"PlainText", 
           
             "content": "Thank you! We will send you the ride details 10 minutes before your ride. " 
            } 
        } 
    }
    
    return lex_response