from fastapi import FastAPI, Depends

from core.aws.dynamodb_client import DynamoDBClient
from core.auth.auth import IsUserOwner
from core.services.services import get_objects, total_objects_count
from core.settings import settings


app = FastAPI()
db = DynamoDBClient


@app.get("/stats/{user_id}", dependencies=[Depends(IsUserOwner())], tags=['stats'])
def retrieve_stats_by_user(user_id: int):
    """
    Return all the stats: posts and pages, number of them and both total likes and followers
    :param user_id: user's profile to view
    :return: dict with the stats.
    """
    page_sort_key = 'owner_id'  # Objects in the db is sorted by this value
    post_filter_key = 'page'  # Local posts' sort key to determine a post's ownership
    likes_pk = 'liked_by'
    followers_pk = 'followers'

    pages = get_objects(settings.TABLE_NAME_PAGES, [user_id], page_sort_key)
    pages_id = [int(page) for page in pages]
    posts = get_objects(settings.TABLE_NAME_POSTS, pages_id, post_filter_key)
    total_posts, total_pages = len(posts), len(pages)
    total_likes = total_objects_count(posts, likes_pk)
    total_followers = total_objects_count(pages, followers_pk)

    return {'data':
        {
            'posts': posts,
            'pages': pages,
            'total_posts': total_posts,
            'total_pages': total_pages,
            'total_likes': total_likes,
            'total_followers': total_followers
        }
    }
