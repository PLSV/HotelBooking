import os
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import uvicorn
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Q
import pybreaker

app = FastAPI()
hotel_breaker = pybreaker.CircuitBreaker(fail_max= 3, reset_timeout= 60)

host = os.getenv("host")
user_name = os.getenv("userName")
password =os.getenv("password")
index_name = os.getenv("indexName")

es = Elasticsearch(
    [host],
    http_auth=(user_name, password),
)

@app.get("/search")
def search(city: str = None, rating: int = 1):
    try:
        hotels =  search_hotels(city, rating)
        response = JSONResponse(content= hotels, status_code=200, 
                    headers={
                        "Access-Control-Allow-Headers": "*",
                        "Access-Control-Allow-Origin": "*",
                        "Access-Control-Allow-Methods": "*"
                    }, media_type="application/json")
        return response
    except pybreaker.CircuitBreakerError as e:
        print("Circuit is open.")

@hotel_breaker
def search_hotels(city: str, rating: int) :
    rating = rating or 1

    s = Search(using=es, index=os.environ.get("indexName"))

    # match all
    # exact match
    # prefix (begins with)
    # fuzzy 
    # range (number)
    
    if city is None:
        s = s.query(Q("match_all") & Q("range", Rating={"gte": rating}))
    else:
        s = s.query(
            Q("prefix", CityName={"value": city.lower()})
            & Q("range", Rating={"gte": rating})
        )
    response = s.execute()
    hotels = [hit["_source"].to_dict() for hit in response.hits.hits]
    return hotels

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=80)