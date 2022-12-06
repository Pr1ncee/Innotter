from fastapi import APIRouter

from api.v1.stats import stats_router


api_v1 = APIRouter(prefix='/v1')

api_v1.include_router(stats_router)
