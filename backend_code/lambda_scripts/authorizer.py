import json
from typing import List, Dict, Any
import boto3
import jwt
from jwt import PyJWK

def auth(event, context):
    id_token = event['queryStringParameters']['token']

    id_token_details = jwt.decode(id_token, options={"verify_signature": False})
    id_token_header = jwt.get_unverified_header(id_token)

    kid = id_token_header['kid']
    alg = id_token_header['alg']

    issuer = id_token_details['iss']
    audience = id_token_details['aud']
    user_id = id_token_details['sub']

    response = {
        "principalId": user_id,
        "policyDocument": {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": "execute-api:Invoke",
                    "Effect": "Allow",
                    "Resource": event['methodArn']
                }
            ]
        }
    }

    secrets_client = boto3.client('secretsmanager')

    secret = secrets_client.get_secret_value(SecretId="hotelPavanCognitoKey")
    secret_keys = secret['SecretString']

    jwks = json.loads(secret_keys)

    public_key = next(filter(lambda x: x['kid'] == kid, jwks['keys']))
    jwtKey = PyJWK.from_dict(public_key)

    decoded = jwt.decode(
            id_token, 
            jwtKey.key, 
            algorithms=[alg], 
            issuer=issuer, 
            audience=audience
        )
    
    api_group_mapping = {
        "listadminhotel+": "Admin",
        "admin+": "Admin"
    }
    
    expected_group = next((v for k, v in api_group_mapping.items() if k in event['path']), None)

    if expected_group:
        user_group = id_token_details.get('cognito:groups', None)
        if user_group and expected_group not in user_group:
            response['policyDocument']['Statement'][0]['Effect'] = "Deny"

    return response