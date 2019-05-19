import googlemaps
from datetime import datetime, timedelta
from copy import deepcopy
import json
import boto3
import uuid
from boto3.dynamodb.conditions import Key, Attr
from decimal import Decimal
import sys

from pyspark import SparkContext



def add_riders(trip, rider_waypoints, rider_start_time, rider_start_date=None, time_epsilon = 15, distance_epsilon = 50):
  
  # route : trip[route]
  # rider_waypoints : [(start_location, 'new', 'start'),(end_location, 'new', 'end')]
  # rider_start_time : '13:00'
  
  # Trip details
    #print('ADD RIDERS', trip['trip_id'])
    #print('hello1')
    route = trip['route']
    trip_start_time = trip['start_time']
    trip_start_date = trip['start_date']

    # Extract rider details
    rider_start_details, rider_end_details = rider_waypoints

    origin, destination, waypoints = extract_info(route)

    # Find out the orginal distance for the trip
    original_directions_obj = api_call(origin, destination, [])
    original_distance = get_distance(original_directions_obj)
    #print('Original distance', original_distance)
    original_duration = get_leg_durations(original_directions_obj)
    #print('orignal duration', original_duration)
  
  # Generate Permutations of waypoints and check
    n = len(waypoints)
    
    min_distance_epsilon = float('inf')
    valid_ride_present = False
    waypoints_final = None
    
    for i in range(0,n+1):
        #print('-'*10)

        waypoints_tmp = deepcopy(waypoints)
        waypoints_tmp.insert(i, rider_start_details)

        for j in range(i+1, len(waypoints_tmp)+1):

            waypoints_new = deepcopy(waypoints_tmp)
            waypoints_new.insert(j, rider_end_details)

            #print('Permutation : ',  waypoints_new)

            waypoints_new_list = get_waypoints_list(waypoints_new)

            directions_result_obj = api_call(origin, destination, waypoints_new_list)

            trip_distance = get_distance(directions_result_obj)
            leg_durations = get_leg_durations(directions_result_obj)

            #print('Current_distance : ', trip_distance, original_distance, trip_distance,  trip_distance / original_distance,trip['trip_id'])# waypoints_new_list)
            
            #print('Leg durations : ', leg_durations)
            # Distance criteria
            distance_criteria_matched = False
            delta = trip_distance / original_distance
            if delta <= distance_epsilon:
                distance_criteria_matched = True

            # Time Criteria

            time_criteria_matched = True 

            trip_start  = deepcopy(trip_start_time)

            for k in range(len(waypoints_new)):
                
                #print('w[k]', waypoints_new[k])
                r_loc, r_id, r_type = waypoints_new[k]

                if r_type.lower() == 'start':
                    time_to_cover = leg_durations[k] # in minutes

                if r_id=='new':
                    r_start = get_date_object(rider_start_date, rider_start_time)
                else:
                    r_start = get_rider_start_time(r_id)
                    if r_start == 'new_user':
                        r_start = get_date_object(rider_start_date, rider_start_time)
                time_rchd = get_date_object(trip_start_date,trip_start_time) + time_to_cover
                #print('Time values :',r_start, time_rchd, trip['trip_id'], waypoints_new_list)

                if  time_rchd > r_start - timedelta(minutes=time_epsilon) and time_rchd < r_start + timedelta(minutes=time_epsilon):
                    trip_start = time_rchd
                else:
                    time_criteria_matched = False
                    break
            
            #print(time_criteria_matched, distance_criteria_matched)
            if time_criteria_matched and distance_criteria_matched:
                this_distance_epsilon = trip_distance/original_distance
                if this_distance_epsilon < min_distance_epsilon:
                    min_distance_epsilon = this_distance_epsilon
                    waypoints_final = deepcopy(waypoints_new)
                    valid_ride_present = True
                
    if valid_ride_present:
        return min_distance_epsilon,waypoints_final
    # return None if there is no match
    return float('inf'),None


dynamodb = boto3.resource('dynamodb',region_name='us-east-1')
sns = boto3.client('sns',region_name='us-east-1')

def get_trips(rider_day, riders_requested):
    riders_requested  = int(riders_requested)
    print(rider_day, riders_requested)
    
    table = dynamodb.Table('trips')
    print(riders_requested, rider_day)
    response = table.scan(FilterExpression =  Attr('num_riders').gte(riders_requested) ) #Attr('start_date').eq(str(rider_day)) &
    if response['Count'] > 0:
        return response["Items"]
    return None

def extract_info(route):
    waypoints = []   
    for i in range(len(route)):
        if (route[i]['user_role']=='driver'):
            if(route[i]['type']=='start'):
                origin = route[i]['location']
            if(route[i]['type']=='end'):
                destination = route[i]['location']      
        else:
            waypoints.append(  (route[i]['location'], route[i]['user_id'], route[i]['type'])  )
    return origin, destination, waypoints

def api_call(origin, dest, waypoints):
    api_key = 'AIzaSyCrsjtsVHryp0c57QVoN0wjBOaFXhH9oyY'
    gmaps = googlemaps.Client(key=api_key)
    directions_result = gmaps.directions(origin,
                                     dest,
                                     mode="driving",
                                     departure_time='now',
                                     waypoints=waypoints,
                                     alternatives=True,
                                     optimize_waypoints=False
                                    )
    #print(directions_result)
    return directions_result

def get_distance(directions_result):
    sum = 0
    for data in directions_result[0]['legs']:
        #0.4 mi
        val = data['distance']['value']
        
        sum += float(val)
        #print(data['start_address'])
        #print(data['end_address'])
        #print(data['duration'], data['distance'])
        #sum += data['distance']['value']
        #print('-'*10)
    return sum
    
def get_leg_durations(directions_result):
    leg_durations = []
    for data in directions_result[0]['legs']:
        #print('asdsad',data['duration']['text'].split(' '))
        val, units = data['duration']['text'].split(' ')
        leg_duration =  timedelta(minutes=int(val))
        leg_durations.append(leg_duration)
    return leg_durations
    
def get_waypoints_list(waypoints):
    retList = []
    for loc,id_,type_ in waypoints:
        retList.append(loc)
    return retList
    
def get_date_object(rider_start_date, rider_start_time):
  # params : strings
  # return : Datetime object
    return datetime.strptime(rider_start_date+' '+rider_start_time, '%Y-%m-%d %H:%M')

def get_rider_start_time(r_id):
  # r_id : User ID of rider
  # get start time in datetime format from the DB
  # return datetime object

    ridertable = dynamodb.Table('riders')
    response = ridertable.get_item(Key={'rider_id' : str(r_id)})
    #print('response:',response)
    if 'Item' in response.keys():
        rider = response['Item']
        start_time = rider['start_time']
        start_date = rider['start_date']
        return get_date_object(start_date, start_time)
    else:
        return 'new_user'
    
def create_route(user_role, location, type_, user_id):
    route = {'user_role': user_role,
    'location': location,
    'type': type_,
    'user_id': user_id}
    
    return route
    
#update trips table with new route info
def update_trips_table(trip_id, route_new, num_riders_new):
    
    table = boto3.resource('dynamodb',region_name='us-east-1').Table('trips')
    response = table.update_item(Key={'trip_id': trip_id},UpdateExpression="set route = :r, num_riders = :n",
            ExpressionAttributeValues={':r': route_new, ':n' : num_riders_new},ReturnValues="UPDATED_NEW")
    #table.update_item(Key={'trip_id': trip_id},AttributeUpdates={'route': route_new, 'num_riders' :  num_riders_new})
    print('Done updating trips!', response)

# Add rider to rider table 
def insert_rider_table(new_rider_id, rider):
    ddb = boto3.client('dynamodb',region_name='us-east-1')
    response = ddb.put_item(TableName = 'riders', Item=rider)
    print('Put')
    print(response)
    
def lex_response(text):
    
    lex_r = { 
        "dialogAction": 
        { 
        "type":"Close", 
        "fulfillmentState":'Fulfilled', 
        "message":{ 
            "contentType":"PlainText", 
           
             "content": text
            } 
        } 
    }
    print('Lex response done')
    return lex_r
    
def send_message_to(d, queue_url):
    print('In send_message_to', json.dumps(d))
    sqs_client = boto3.client('sqs',region_name='us-east-1')
    response = sqs_client.send_message(
        QueueUrl=queue_url,
        MessageBody=json.dumps(d),
        DelaySeconds=0)
    return response

def get_user_details(username):
    dynamodb = boto3.resource('dynamodb',region_name='us-east-1')
    table = dynamodb.Table('users')
    response = table.scan(FilterExpression=Key('username').eq(username))#, ProjectionExpression='#number')
    if response['Count']>0:
        return response['Items'][0]['number']
    else:
        return 'User not found'
        
def send_sms_to_rider(username, message):
    
    if message[0]==':':
        driver_user_name = message[1:]
        driver_phone_number = get_user_details(driver_user_name)
        driver_image_url = 'https://s3.amazonaws.com/cloudcomputingcolumbiaproject/'+driver_user_name+'.jpg'
        message = 'You have been matched with driver ' + driver_user_name + ', Phone number : ' + driver_phone_number + ', URL : ' + driver_image_url
    phone_number = get_user_details(username)
    sns.publish(PhoneNumber = phone_number, Message= message)
    print('SMS sent to ', phone_number[2:], message)
    

if __name__ == "__main__":
    """
        Usage: pi [partitions]
    """
    sc = SparkContext(appName="PythonPi")
    client = boto3.client('sqs',region_name='us-east-1')
    queue_url = 'https://sqs.us-east-1.amazonaws.com/044634429688/RiderQueue'
    response = client.receive_message(
        QueueUrl=queue_url,
        AttributeNames=['All'],
        MessageAttributeNames=[
            'string',
        ],
        MaxNumberOfMessages=1,
        VisibilityTimeout=0,
        WaitTimeSeconds=10,
    )
    if (len(response['Messages'])>0):

        
        receipt_handle = response['Messages'][0]['ReceiptHandle']
        rider_info_string = response['Messages'][0]['Body']
        print(rider_info_string)
        rider = json.loads(rider_info_string)
        
        start_date = rider['start_date']
        start_time = rider['start_time']
        num_riders = rider['num_riders']
        new_rider_id = rider['rider_id']
        from_address = rider['from']
        to_address = rider['to']
        username = rider['username']
        city = rider['city']
        matched = rider['matched']

        rider_write = {'from': {'S': from_address}, 
                        'to': {'S': to_address},
                        'start_date': {'S': start_date},
                        'start_time': {'S': start_time},
                        'num_riders': {'N': str(num_riders)}, 
                        'rider_id': {'S': new_rider_id}, 
                        'city': {'S': city}, 
                        'matched': {'S': matched}, 
                        'username': {'S': username}}

        trips = get_trips(start_date, num_riders)        

        rider_start = get_date_object(start_date, start_time)

        def map_f(trip):
            import googlemaps
            from datetime import datetime
            from copy import deepcopy
            import json
            import boto3
            import uuid
            from boto3.dynamodb.conditions import Key, Attr
            from decimal import Decimal

            def add_riders(trip, rider_waypoints, rider_start_time, rider_start_date=None, time_epsilon = 15, distance_epsilon = 50):
                # route : trip[route]
                # rider_waypoints : [(start_location, 'new', 'start'),(end_location, 'new', 'end')]
                # rider_start_time : '13:00'
                
                # Trip details
                #print('ADD RIDERS', trip['trip_id'])
                #print('hello1')
                route = trip['route']
                trip_start_time = trip['start_time']
                trip_start_date = trip['start_date']

                # Extract rider details
                rider_start_details, rider_end_details = rider_waypoints

                origin, destination, waypoints = extract_info(route)

                # Find out the orginal distance for the trip
                original_directions_obj = api_call(origin, destination, [])
                original_distance = get_distance(original_directions_obj)
                #print('Original distance', original_distance)
                original_duration = get_leg_durations(original_directions_obj)
                #print('orignal duration', original_duration)
            
                # Generate Permutations of waypoints and check
                n = len(waypoints)
                
                min_distance_epsilon = float('inf')
                valid_ride_present = False
                waypoints_final = None
                
                for i in range(0,n+1):
                    #print('-'*10)

                    waypoints_tmp = deepcopy(waypoints)
                    waypoints_tmp.insert(i, rider_start_details)

                    for j in range(i+1, len(waypoints_tmp)+1):

                        waypoints_new = deepcopy(waypoints_tmp)
                        waypoints_new.insert(j, rider_end_details)

                        #print('Permutation : ',  waypoints_new)

                        waypoints_new_list = get_waypoints_list(waypoints_new)

                        directions_result_obj = api_call(origin, destination, waypoints_new_list)

                        trip_distance = get_distance(directions_result_obj)
                        leg_durations = get_leg_durations(directions_result_obj)

                        #print('Current_distance : ', trip_distance, original_distance, trip_distance,  trip_distance / original_distance,trip['trip_id'])# waypoints_new_list)
                        
                        #print('Leg durations : ', leg_durations)
                        # Distance criteria
                        distance_criteria_matched = False
                        delta = trip_distance / original_distance
                        if delta <= distance_epsilon:
                            distance_criteria_matched = True

                        # Time Criteria

                        time_criteria_matched = True 

                        trip_start  = deepcopy(trip_start_time)

                        for k in range(len(waypoints_new)):
                            
                            #print('w[k]', waypoints_new[k])
                            r_loc, r_id, r_type = waypoints_new[k]

                            if r_type.lower() == 'start':
                                time_to_cover = leg_durations[k] # in minutes

                            if r_id=='new':
                                r_start = get_date_object(rider_start_date, rider_start_time)
                            else:
                                r_start = get_rider_start_time(r_id)
                                if r_start == 'new_user':
                                    r_start = get_date_object(rider_start_date, rider_start_time)
                            time_rchd = get_date_object(trip_start_date,trip_start_time) + time_to_cover
                            #print('Time values :',r_start, time_rchd, trip['trip_id'], waypoints_new_list)

                            if  time_rchd > r_start - timedelta(minutes=time_epsilon) and time_rchd < r_start + timedelta(minutes=time_epsilon):
                                trip_start = time_rchd
                            else:
                                time_criteria_matched = False
                                break
                        
                        #print(time_criteria_matched, distance_criteria_matched)
                        if time_criteria_matched and distance_criteria_matched:
                            this_distance_epsilon = trip_distance/original_distance
                            if this_distance_epsilon < min_distance_epsilon:
                                min_distance_epsilon = this_distance_epsilon
                                waypoints_final = deepcopy(waypoints_new)
                                valid_ride_present = True
                            
                if valid_ride_present:
                    return min_distance_epsilon,waypoints_final
                # return None if there is no match
                return float('inf'),None

            dynamodb = boto3.resource('dynamodb',region_name='us-east-1')
            sns = boto3.client('sns',region_name='us-east-1')

            def get_trips(rider_day, riders_requested):
                riders_requested  = int(riders_requested)
                print(rider_day, riders_requested)
                
                table = dynamodb.Table('trips')
                print(riders_requested, rider_day)
                response = table.scan(FilterExpression =  Attr('num_riders').gte(riders_requested) ) #Attr('start_date').eq(str(rider_day)) &
                if response['Count'] > 0:
                    return response["Items"]
                return None

            def extract_info(route):
                waypoints = []   
                for i in range(len(route)):
                    if (route[i]['user_role']=='driver'):
                        if(route[i]['type']=='start'):
                            origin = route[i]['location']
                        if(route[i]['type']=='end'):
                            destination = route[i]['location']      
                    else:
                        waypoints.append(  (route[i]['location'], route[i]['user_id'], route[i]['type'])  )
                return origin, destination, waypoints

            def api_call(origin, dest, waypoints):
                api_key = 'AIzaSyCrsjtsVHryp0c57QVoN0wjBOaFXhH9oyY'
                gmaps = googlemaps.Client(key=api_key)
                directions_result = gmaps.directions(origin,
                                                dest,
                                                mode="driving",
                                                departure_time='now',
                                                waypoints=waypoints,
                                                alternatives=True,
                                                optimize_waypoints=False
                                                )
                #print(directions_result)
                return directions_result

            def get_distance(directions_result):
                sum = 0
                for data in directions_result[0]['legs']:
                    #0.4 mi
                    val = data['distance']['value']
                    
                    sum += float(val)
                    #print(data['start_address'])
                    #print(data['end_address'])
                    #print(data['duration'], data['distance'])
                    #sum += data['distance']['value']
                    #print('-'*10)
                return sum
                
            def get_leg_durations(directions_result):
                leg_durations = []
                for data in directions_result[0]['legs']:
                    #print('asdsad',data['duration']['text'].split(' '))
                    val, units = data['duration']['text'].split(' ')
                    leg_duration =  timedelta(minutes=int(val))
                    leg_durations.append(leg_duration)
                return leg_durations
                
            def get_waypoints_list(waypoints):
                retList = []
                for loc,id_,type_ in waypoints:
                    retList.append(loc)
                return retList
                
            def get_date_object(rider_start_date, rider_start_time):
                # params : strings
                # return : Datetime object
                return datetime.strptime(rider_start_date+' '+rider_start_time, '%Y-%m-%d %H:%M')

            def get_rider_start_time(r_id):
                # r_id : User ID of rider
                # get start time in datetime format from the DB
                # return datetime object

                ridertable = dynamodb.Table('riders')
                response = ridertable.get_item(Key={'rider_id' : str(r_id)})
                #print('response:',response)
                if 'Item' in response.keys():
                    rider = response['Item']
                    start_time = rider['start_time']
                    start_date = rider['start_date']
                    return get_date_object(start_date, start_time)
                else:
                    return 'new_user'
                
            def create_route(user_role, location, type_, user_id):
                route = {'user_role': user_role,
                'location': location,
                'type': type_,
                'user_id': user_id}
                
                return route
                
            #update trips table with new route info
            def update_trips_table(trip_id, route_new, num_riders_new):
                
                table = boto3.resource('dynamodb',region_name='us-east-1').Table('trips')
                response = table.update_item(Key={'trip_id': trip_id},UpdateExpression="set route = :r, num_riders = :n",
                        ExpressionAttributeValues={':r': route_new, ':n' : num_riders_new},ReturnValues="UPDATED_NEW")
                #table.update_item(Key={'trip_id': trip_id},AttributeUpdates={'route': route_new, 'num_riders' :  num_riders_new})
                print('Done updating trips!', response)

            # Add rider to rider table 
            def insert_rider_table(new_rider_id, rider):
                ddb = boto3.client('dynamodb',region_name='us-east-1')
                response = ddb.put_item(TableName = 'riders', Item=rider)
                print('Put')
                print(response)
                
            def lex_response(text):
                
                lex_r = { 
                    "dialogAction": 
                    { 
                    "type":"Close", 
                    "fulfillmentState":'Fulfilled', 
                    "message":{ 
                        "contentType":"PlainText", 
                    
                        "content": text
                        } 
                    } 
                }
                print('Lex response done')
                return lex_r
                
            def send_message_to(d, queue_url):
                print('In send_message_to', json.dumps(d))
                sqs_client = boto3.client('sqs',region_name='us-east-1')
                response = sqs_client.send_message(
                    QueueUrl=queue_url,
                    MessageBody=json.dumps(d),
                    DelaySeconds=0)
                return response

            def get_user_details(username):
                dynamodb = boto3.resource('dynamodb',region_name='us-east-1')
                table = dynamodb.Table('users')
                response = table.scan(FilterExpression=Key('username').eq(username))#, ProjectionExpression='#number')
                if response['Count']>0:
                    return response['Items'][0]['number']
                else:
                    return 'User not found'
                    
            def send_sms_to_rider(username, message):
                
                if message[0]==':':
                    driver_user_name = message[1:]
                    driver_phone_number = get_user_details(driver_user_name)
                    driver_image_url = 'https://s3.amazonaws.com/cloudcomputingcolumbiaproject/'+driver_user_name+'.jpg'
                    message = 'You have been matched with driver ' + driver_user_name + ', Phone number : ' + driver_phone_number + ', URL : ' + driver_image_url
                phone_number = get_user_details(username)
                sns.publish(PhoneNumber = phone_number, Message= message)
                print('SMS sent to ', phone_number[2:], message)
            
    
            # start_date = '2019-05-11'
            # start_time = '13:00'
            trip_id = trip['trip_id']
            waypoints_new = None
            distance_epsilon = float('inf')
            #print(trip_id)
            trip_start = get_date_object(trip['start_date'], trip['start_time'])
            if rider_start >= trip_start or trip_start >= rider_start + timedelta(hours=1):
                #print('Here000000',trip_id)
                rider_waypoints = [(from_address, new_rider_id, 'start'),(to_address, new_rider_id, 'end')]
                distance_epsilon, waypoints_new = add_riders(trip, rider_waypoints, start_time, start_date)
                
            return (trip_id, (waypoints_new, distance_epsilon), trip)

        def reduce_f(a,b):
            if a[1][1] > b[1][1]:
                return b
            return a
        add_to_queue = True    
        #print('Trips',len(trips))
        if trips:
            count = sc.parallelize(trips, 1).map(map_f).reduce(reduce_f)
            matched_trip_id, waypoint_details, matched_trip = count
            waypoints_matched, distance_epsilon = waypoint_details
            if waypoints_matched and len(waypoints_matched) > 0 :
                # There is a matching trip
                route_new = []
                route_new.append(create_route('driver', matched_trip['from'], 'start', matched_trip_id))
                for i in range(len(waypoints_matched)):
                    route_new.append(create_route('rider', waypoints_matched[i][0], waypoints_matched[i][2], waypoints_matched[i][1]))
                route_new.append(create_route('driver', matched_trip['to'], 'end', matched_trip_id))
                print(route_new)
                rider_write['matched']['S'] = 'true'
                rider['matched'] = 'true'
                new_capacity = Decimal(int(matched_trip['num_riders']) - int(num_riders))
                print('New capacity', new_capacity)
                #update trips table with new route info
                update_trips_table(matched_trip_id, route_new, new_capacity)
                # Add rider to rider table with status as matched
                insert_rider_table(new_rider_id, rider_write)
                send_sms_to_rider(username, ':'+matched_trip['username'])
                #print(lex_response('ride found!' + matched_trip_id+ ' driver is ' + matched_trip['username']))
                add_to_queue = False
            else:
                add_to_queue = True
        if add_to_queue:
            q_response = send_message_to(rider,queue_url)
            print('Q response', q_response)
            #send_sms_to_rider(username, 'You have been placed in the queue!')
        
        client.delete_message(
            QueueUrl=queue_url,
        ReceiptHandle=receipt_handle
        )

    print('Done!')

    sc.stop()

    