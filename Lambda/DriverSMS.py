import json
import boto3
from boto3.dynamodb.conditions import Key, Attr
from datetime import datetime, timedelta

def get_date_object(rider_start_date, rider_start_time):
  # params : strings
  # return : Datetime object
    return datetime.strptime(rider_start_date+' '+rider_start_time, '%Y-%m-%d %H:%M')
    
def get_user_details(username):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('users')
    response = table.scan(FilterExpression=Key('username').eq(username))#, ProjectionExpression='#number')
    if response['Count']>0:
        return response['Items'][0]['number']
    else:
        return 'User not found'
        
def beautify_message(route):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('riders')
    
    str_= 'Hi there! Your ride is about to start. The details of your ride are: \n'
    
    
    waypoint_str  = ''
    for i in range(len(route)):
        str_ += str(i+1)+'. '
        waypoint_str += '/'+route[i]['location']
        
        if route[i]['user_role']=='driver':
            if route[i]['type'] == 'start': 
                str_+= 'Start from '+ route[i]['location']+ '\n'
            elif route[i]['type']== 'end':

                str_+= 'End your trip at '+ route[i]['location']+ '\n'
        else:
            response = table.scan(FilterExpression=Key('rider_id').eq(route[i]['user_id']))
            username = response['Items'][0]['username']
            if route[i]['type'] == 'start':

                str_+= 'Pickup '+username+' from '+route[i]['location']+'\n'

            elif route[i]['type']== 'end':
                str_+= 'Dropoff '+username+' at '+route[i]['location']+'\n'
        
    link = 'https://www.google.com/maps/dir'+waypoint_str
    link = link.replace(' ','+')
                
    str_+= 'You can find the route for your trip and the estimated times at:  '+ link

    return str_

def lambda_handler(event, context):
    # TODO implement
    sns = boto3.client('sns')
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('trips')
    response = table.scan(ProjectionExpression='username, start_time, start_date, route')
    time_epsilon = 600 # Send driver SMS 10 min prior to start time
    time_zone_adjustment = timedelta(hours=4)
    curr_time = datetime.now() - time_zone_adjustment
    #print(curr_time)
    if response['Count'] > 0:
        trips = response["Items"]
        for trip in trips:
            print(trip['start_date'], trip['start_time'])
            trip_start_time = get_date_object(trip['start_date'], trip['start_time'])
            diff = (trip_start_time - curr_time).total_seconds()
            print(diff)
            if  diff >= 0 and diff <= time_epsilon:
                message_to_send =  beautify_message(trip['route'])
                phone_number = get_user_details(trip['username'])
                sns.publish(PhoneNumber = phone_number, Message= message_to_send)
                print('sent to ', phone_number, trip['username'])
    else:       
        return 'NO Drivers in DB'
    
    # return {
    #     'statusCode': 200,
    #     'body': json.dumps('Hello from Lambda!')
    # }
