from core.aws.dynamodb_client import DynamoDBClient
from core.auth.auth import JWTBearer
from core.settings import settings
from fastapi import FastAPI, Depends


# TODO replace warnings with logging

app = FastAPI()
db = DynamoDBClient


@app.get("/stats/{user_id}", dependencies=[Depends(JWTBearer())], tags=['stats'])
def retrieve_stats_by_user(user_id: int):
    return {'data': 'In development...'}
