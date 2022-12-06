from pydantic import BaseModel


class Stats(BaseModel):
    posts: dict
    pages: dict
    total_posts: int
    total_pages: int
    total_likes: int
    total_followers: int

    class Config:
        orm_mode = True
