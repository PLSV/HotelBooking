import os
import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import boto3

app = FastAPI()

# Allow cross-origin resource sharing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Handle POST requests to /approve
@app.post('/approve')
async def approve(booking_id: str, status: int):
    topic_arn = os.getenv('topicArn') 
    sns = boto3.client('sns')
    response = sns.publish(
            TopicArn=topic_arn,
            Message=json.dumps({'bookingId': booking_id, 'status': status})
        )   
    return JSONResponse(status_code=200, 
                        content=json.dumps({'message': 'Approval event published'}),
                        media_type="application/json")


# Health Check 
@app.get('/health')
async def health_check():
    return JSONResponse(status_code=200, content="OK")

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)