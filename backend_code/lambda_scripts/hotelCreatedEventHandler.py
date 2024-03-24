import json
import os
import boto3
from boto3 import dynamodb
from boto3.dynamodb.conditions import Key
from elasticsearch import Elasticsearch

def handler(event, context):
    sns_message = event['Record'][0]['Sns']['Message']
    sns_message_json = json.loads(sns_message)
    message_id = sns_message_json["MessageId"]

    tableName = os.environ.get("hotelCreatedEventIdsTable")
    
    dynamodb_client = boto3.client('dynamodb')
    response = dynamodb_client.get_item(
        TableName = tableName,
        Key = {
            "eventId": {
                "S": message_id
            }
        }
    )

    if 'Items' not in response:
        dynamodb_client.put_item(
            TableName=tableName,
            Item = {
                "eventId": {
                    "S": message_id
                }
            }
        )

        host = os.getenv("host")
        user_name = os.getenv("userName")
        password =os.getenv("password")
        index_name = os.getenv("indexName")

        es = Elasticsearch(host, http_auth=(user_name, password))
        es.index(index=f"{index_name}", id=sns_message_json["Id"], body=sns_message_json)