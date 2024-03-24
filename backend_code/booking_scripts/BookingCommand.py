import json
import os
import uuid
from enum import Enum
import jwt
import boto3
from boto3.dynamodb.conditions import Key
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

class BookingStatus(int, Enum):
    Pending = 1
    Confirmed = 2
    Rejected = 3

class request_model(BaseModel):
    checkinDate: str
    checkoutDate: str
    idToken: str
    hotelId: str

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_headers=["*"],
    allow_methods=["*"]
)

@app.post("/book")
def book(request:request_model):
    token = request.idToken  # JWT Token
    id_token_details = jwt.decode(token, options={"verify_signature": False})

    booking = {
        "Id": str(uuid.uuid4()),
        "HotelId": request.hotelId,
        "CheckinDate": request.checkinDate,
        "CheckoutDate": request.checkoutDate,
        "UserId": id_token_details.get("sub"),
        "GivenName": id_token_details.get("given_name"),
        "FamilyName": id_token_details.get("family_name"),
        "PhoneNumber": id_token_details.get("phone_number"),
        "Email": id_token_details.get("email"),
        "Status": BookingStatus.Pending
    }

    table_name= os.getenv("tableName")
    client = boto3.resource("dynamodb")
    table = client.Table(table_name)
    table.put_item(Item=booking)

    return JSONResponse(status_code=200, content=json.dumps({"Status":BookingStatus.Pending}))

@app.get("/health")
def health_check():
    return JSONResponse(status_code= 200, content="OK")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=80)