# import json
# import boto3
# def lambda_handler(event, context):
#     # TODO implement
#     client = boto3.client('lex-runtime')
#     bot = 'Rider'
#     response = client.post_text(botName=bot, botAlias='Rider', userId='shruti', inputText='Hey')
#     return {
#             'headers': {
#                 "Access-Control-Allow-Credentials" : "*",
#                 "Access-Control-Allow-Origin": "*",
#             },
#             'statusCode': 200,
#             'body': json.dumps(response["message"])
#         }



import json
import boto3

import math
import datetime
import time
import os
import dateutil.parser
import logging
import hashlib

# logger = logging.getLogger()
# logger.setLevel(logging.DEBUG)

def get_user_input_from_request(event):
    """Retrieve the user's message and username from the incoming request.
    
    Args:
        event (dict): The event that triggered this Lambda function.
        
    Returns:
        A string, string tuple with the message, followed by the username from cognito.
    """

    # if 'body' not in event:
    #     logger.error('Malformed HTTP Request body given')
    #     logger.error(event)
    #     return None, None
    
    # #body = event['body']
    # try:
    #     body = json.loads(body)
    # except json.JSONDecodeError:
    #     logger.error('Malformed body message sent. Must be valid JSON string.')
    #     logger.error(body)
    #     return None, None
        
    # if 'messages' not in body:
    #     logger.error('Body must contain "messages" key')
    #     return None, None
    
    # messages = body['messages']
    # if not isinstance(messages, list) or len(messages) < 1:
    #     logger.error('There are no messages')
    #     return None, None
    
    # message = messages[0]
    # if 'unstructured' not in message:
    #     logger.error('message object missing "unstructured" key')
    #     return None, None
    
    # if 'text' not in message['unstructured'] or 'id' not in message['unstructured']:
    #     logger.error('Message is missing text or id')
    #     return None, None
        
    # text = message['unstructured']['text']

    # #user_id = event['requestContext']['authorizer']['claims']['cognito:username']
    # # Use the session as a proxy for user ID
    # user_id = event['requestContext']['identity']['user']
    text = event['body']
    user_id = event['userID']
    return text, user_id

def get_chatbot_response(user_input, user_id):
    """Return the response message from the chatbot.
    
    Args:
        user_input (string): User's message
        user_id (string): The Username
        
    Returns:
        The string response message from the chatbot.
    """
    
    message = ''
    client = boto3.client('lex-runtime')
    lex_response = client.post_text(
        botName='ConciergeSevice',
        botAlias='Dining',
        userId=user_id,
        inputText=user_input
    )
    
    if not isinstance(lex_response,dict):
        # logger.error('Lex Response is not a dictionary')
        return None
    
    if 'message' not in lex_response:
        # logger.error('Lex Response missing the "message" key')
        return None
        
    message = lex_response['message']
    # 
    
    # logger.debug('Lex Message: {}'.format(message))
    return message
    
def get_chatbot_response_from_rider(user_input, user_id):
    """Return the response message from the chatbot.
    
    Args:
        user_input (string): User's message
        user_id (string): The Username
        
    Returns:
        The string response message from the chatbot.
    """
    
    message = ''
    client = boto3.client('lex-runtime')
    lex_response = client.post_text(
        botName='Driver_bot',
        botAlias='Driver',
        userId=user_id,
        inputText=user_input
    )
    
    if not isinstance(lex_response,dict):
        # logger.error('Lex Response is not a dictionary')
        return None
    
    if 'message' not in lex_response:
        # logger.error('Lex Response missing the "message" key')
        return None
        
    message = lex_response['message']
    # logger.debug('Lex Message: {}'.format(message))
    return message
    
def get_success_body(message):
    """Return response body in the case of a successful response from the chatbot.
    
    Args:
        message (string): Text message to include in the response.
    
    Returns:
        Dictionary with the expected response body as defined in the Swagger document.
    """

    body = {
        "messages": [{
                "type": "BotMessage",
                "unstructured": {
                    "id": None,
                    "text": message,
                    "timestamp": time.time()
                }
            }
        ]
    }
    return body;
    
def get_error_body(error):
    """Return response body in the case of an error.
    
    Args:
        error (string): Text message to include in the response.
    
    Returns:
        Dictionary with the expected response body as defined in the Swagger document.
    """

    body = {
        "messages": [{
                "type": "BotMessage",
                "unstructured": {
                    "id": None,
                    "text": error,
                    "timestamp": time.time()
                }
            }
        ]
    }
    return body;
    
def get_api_response(body):
    """Return the complete API response for the endpoint, including the given body.
    
    Args:
        body (dict): Response body.
        
    Returns:
        Dict containing the response code, headers, body.
    """

    response = {
        "statusCode": 200,
        "headers": {
           
            "Access-Control-Allow-Origin": "*",
        },
        "body": json.dumps(body),
        "isBase64Encoded": False
    }
    return response

def get_md5(my_string):
    """Return the MD5 one-way hash of the given input string.
    
    Args:
        my_string (string): The string to make a hash of.
    
    Returns:
        string: The MD5 hash
    """

    return hashlib.md5(my_string.encode('utf-8')).hexdigest()
    
def get_chatbot_response_from_rider(user_input, user_id):
    message = ''
    client = boto3.client('lex-runtime')
    lex_response = client.post_text(
        botName='Driver_bot',
        botAlias='Driver',
        userId=user_id,
        inputText=user_input
    )
    
    if not isinstance(lex_response,dict):
        # logger.error('Lex Response is not a dictionary')
        return None
    
    if 'message' not in lex_response:
        # logger.error('Lex Response missing the "message" key')
        return None
        
    message = lex_response['message']
    # logger.debug('Lex Message: {}'.format(message))
    return message

    
def lambda_handler(event, context):
    print("Driver Called")
    # logger.debug('Starting Python Version Now')
    # logger.error("Logging the input request")
    #logger.error(event)
    # Get the user's message and name
    text, user_id = get_user_input_from_request(event)
    # logger.debug('User ID: {}; Text: {}'.format(user_id, text))
    user_id = json.loads(user_id)["username"]
    print(user_id)
    if text is None or user_id is None:
        body = get_error_body("Unable to parse User ID or text from Request")
        return get_api_response(body)
    
    # Hash the user identity and get a response from the bot
    # user_id = get_md5(user_id)
    message = get_chatbot_response_from_rider(user_input=text, user_id=user_id)

    # Send the response back to the API Gateway
    body = None
    if (message is not None):
        body = get_success_body(message)
    else:
        body = get_error_body("Done")
    response = get_api_response(body)
    return response
    
