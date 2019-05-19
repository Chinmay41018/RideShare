from datetime import datetime
from copy import deepcopy
import json
import boto3
import uuid
import sys
import time

def lambda_handler(event, context):
    
    username = event['userId']
    
    from_address = event["currentIntent"]["slots"]["FromLocation"]
    to_address = event["currentIntent"]["slots"]["ToLocation"]
    start_date = event["currentIntent"]["slots"]["startDate"]
    start_time = event["currentIntent"]["slots"]["startTime"]
    num_riders = event["currentIntent"]["slots"]["numRiders"]
    city = event["currentIntent"]["slots"]["city"]
    
    new_rider_id = str(uuid.uuid1())
    
    rider = {'from': {'S': from_address}, 
          'to': {'S': to_address},
          'start_date': {'S': str(start_date)},
          'start_time': {'S' : start_time}, 
          'num_riders': {'N': num_riders} ,
          'rider_id' : {'S': new_rider_id},
          'city': {'S' : city},
          'matched' : {'S' : 'false'},
          'username' : {'S' :  username}
         }
    
    conn = boto3.client("emr")
    # chooses the first cluster which is Running or Waiting
    # possibly can also choose by name or already have the cluster id
    clusters = conn.list_clusters()
    # choose the correct cluster
    clusters = [c["Id"] for c in clusters["Clusters"] 
                if c["Status"]["State"] in ["RUNNING", "WAITING"]]
    if not clusters:
        sys.stderr.write("No valid clusters\n")
        sys.stderr.exit()
    # take the first relevant cluster
    cluster_id = clusters[0]
    # code location on your emr master node
    CODE_DIR = "/home/hadoop/"

    # spark configuration example
    step_args = ["/usr/bin/spark-submit", "", "",
                 CODE_DIR + "spark_main.py", '', json.dumps(rider)]

    step = {"Name": "what_you_do-" + time.strftime("%Y%m%d-%H:%M"),
            'ActionOnFailure': 'CONTINUE',
            'HadoopJarStep': {
                'Jar': 's3n://elasticmapreduce/libs/script-runner/script-runner.jar',
                'Args': step_args
            }
        }
    action = conn.add_job_flow_steps(JobFlowId=cluster_id, Steps=[step])
    lex_response = { 
        "dialogAction": 
        { 
        "type":"Close", 
        "fulfillmentState":'Fulfilled', 
        "message":{ 
            "contentType":"PlainText", 
           
             "content": "You will recieve a message soon!"
            } 
        } 
    }
    return lex_response
