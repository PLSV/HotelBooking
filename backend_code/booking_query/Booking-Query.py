import os
import jwt #pyjwt
import boto3
from enum import Enum
from boto3.dynamodb.conditions import Key
from dynamodb_json import json_util as ddb_json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi import Query
import uvicorn

class BookingStatus(int, Enum):
    Pending = 1
    Confirmed = 2
    Rejected = 3

app = FastAPI()
app.add_middleware(CORSMiddleware,
    allow_origins=["*"],
    allow_headers=["*"],
    allow_methods=["*"])

@app.get('/query')
def query(id_token: str = Query(alias="idToken") ):
    id_token_details = jwt.decode(id_token, options={"verify_signature": False})

    user_id = id_token_details.get('sub', '')
    groups = id_token_details.get('cognito:groups', '')

    result = []

    booking_table_name = os.getenv('tableName')
    hotel_table_name = os.getenv("hotelOrderDomainTableName")

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(booking_table_name)

    if not groups: # ordinary user
        response = table.query(
            IndexName='UserId-index',
            KeyConditionExpression=Key('UserId').eq(user_id)
        )
        result.extend(response['Items'])
    else:
        if 'HotelManager' in groups: # hotel admin
            response = table.query(
                IndexName='Status-index',
                KeyConditionExpression=Key('Status').eq(BookingStatus.Pending)
            )
            result.extend(response['Items'])

    # Additional code to display extra information (not part of the lecture)
    hotel_table = dynamodb.Table(hotel_table_name)
    for booking in result:
        hotel_id = booking['HotelId']
        response = hotel_table.query(
            IndexName='Id-index',
            KeyConditionExpression=Key('Id').eq(hotel_id)
        )
        matching_hotels = response['Items']
        matching_hotel = matching_hotels[0] if len(matching_hotels) >0 else None
        if matching_hotel:
            booking['HotelName'] = matching_hotel.get('Name', '')
            booking['CityName'] = matching_hotel.get('CityName', '') 

    json_result = ddb_json.loads(result)
    return JSONResponse(status_code= 200, content=json_result, media_type="application/json")

@app.get("/health")
def health_check():
    return JSONResponse(status_code= 200, content="OK")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8223)