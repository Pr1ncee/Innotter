from fastapi import APIRouter
from api.v1.router import api_v1


base_router = APIRouter(prefix='/api')

base_router.include_router(api_v1)
