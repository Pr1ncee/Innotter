from typing import Type

from fastapi import APIRouter, Depends

from api.schemas.stats_schema import Stats
from core.auth.jwt_middleware import IsUserOwner
from core.services.stats_service import StatisticsService


stats_router = APIRouter(tags=['stats'])


@stats_router.get("/stats/{user_id}", dependencies=[Depends(IsUserOwner())], response_model=Stats)
def retrieve_stats_by_user(user_id: int) -> Type[Stats]:
    """
    Return all the Stats: posts and pages, number of them and both total likes and followers
    :param user_id: user's profile to view
    :return: dict with the Stats.
    """
    response = StatisticsService.processing_stats(user_id)
    return response
