import json
import os
import boto3

def handler(event, context):
    # To implement Idempotent Consumer pattern
    message_id = event['Records'][0]['Sns']['MessageId']

    sns_message = event['Records'][0]['Sns']['Message']
    sns_message_json = json.loads(sns_message)

    hotels_order_domain_table = os.getenv('hotelsOrderDomain')

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(hotels_order_domain_table)
    table.put_item(Item=sns_message_json)