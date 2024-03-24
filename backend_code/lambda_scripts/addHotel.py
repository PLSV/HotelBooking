import json
import boto3
import logging
import multipart
import base64
import jwt
import os
import uuid

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

def handler(event, context):
    headers = {
        "Access-Control-Allow-Headers": "*",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "*"
    }
    
    body = event['body']

    if bool(event.get('isBase64Encoded')):
        body = base64.b64decode(body)
    else:
        body = body.encode('utf-8')

    parser = multipart.FormDataParser(body)
    parts = parser.parse()

    hotel_name = parts.get('hotelName')
    hotel_rating = parts.get('hotelRating')
    hotel_city = parts.get('hotelCity')
    hotel_price = parts.get('hotelPrice')
    file_name = parts.get('fileName')
    user_id = parts.get('userId')
    id_token = parts.get('idToken')

    file = parts.get('fileData').file.read()

    token = jwt.decode(id_token, options={"verify_signature": False})
    group = token.get('cognito:groups')

    logger.info(group)

    if group is None or 'Admin' not in group:
        return {
            'statusCode': 401,
            'headers':response_headers,
            'body': json.dumps({
                'Error': 'You are not a member of the Admin group'
            })
        }

    bucket_name = os.environ.get('bucketName')
    region = os.environ.get('AWS_REGION')

    s3_client = boto3.client("s3", region_name = region)
    dynamoDb = boto3.resource('dynamodb', region_name=region)
    table = dynamoDb.Table('Hotels')
    sns_client = boto3.client('sns')

    try:
        s3_client.put_object(
            Bucket = bucket_name,
            Key = file_name,
            Body = file
        )

        hotel = {
            "userId": user_id,
            "Id": str(uuid.uuid4()),
            "Name": hotel_name,
            "CityName": hotel_city,
            "Price": int(hotel_price),
            "Rating": int(hotel_rating),
            "FileName": file_name
        }

        table.put_item(Item=hotel)

        sns_topic_arn = os.getenv("hotelCreationTopicArn")
        sns_client.publish(
            TopicArn=sns_topic_arn,
            Message= json.dumps(hotel)
        )

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({
                "Error": "Uploading the hotel photo failed"
            })
        }

    logger.debug("Info")
    return {
        'statusCode': 200,
        'headers': headers,
        'body': json.dumps(event['key1'])
    }
