from typing import Type

from api.schemas.stats_schema import Stats
from core.services.services import get_objects, total_objects_count
from core.settings import settings


class StatisticsService:
    _page_sort_key = 'owner_id'  # Objects in the db is sorted by this value
    _post_filter_key = 'page'  # Local posts' sort key to determine a post's ownership
    _likes_pk = 'liked_by'
    _followers_pk = 'followers'

    @classmethod
    def processing_stats(cls, user_id: int) -> Type[Stats]:
        pages = get_objects(settings.PAGES_NAME_TABLE, [user_id], cls._page_sort_key)
        pages_id = [int(page) for page in pages]
        posts = get_objects(settings.POSTS_NAME_TABLE, pages_id, cls._post_filter_key)
        total_posts, total_pages = len(posts), len(pages)
        total_likes = total_objects_count(posts, cls._likes_pk)
        total_followers = total_objects_count(pages, cls._followers_pk)

        Stats.pages = pages
        Stats.posts = posts
        Stats.total_pages = total_pages
        Stats.total_posts = total_posts
        Stats.total_likes = total_likes
        Stats.total_followers = total_followers
        return Stats
