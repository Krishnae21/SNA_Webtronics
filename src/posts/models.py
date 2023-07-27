from pydantic import BaseModel
from typing import Literal
from datetime import datetime
from typing import Any


class Return(BaseModel):
    status: str = "Error"
    details: str = None


class Post(BaseModel):
    title: str
    body: str


class FullPost(Post):
    id: int
    posted_username: str
    posted_at: datetime
    likes: int = 0
    dislikes: int = 0

    def __init__(self, **data: Any):
        super().__init__(**data)
        self.posted_at = self.posted_at.isoformat()


class PostReturn(Return):
    data: FullPost = None


class ReactionReturn(Return):
    type: str = None


class ReactionRequest(BaseModel):
    post_id: int
    type: Literal["Like", "Dislike"]


class ReactionDB(BaseModel):
    reaction: int
    post_id: int
    reactkey: str


class EditRequest(BaseModel):
    post_id: int
    title: str
    body: str


class DeleteRequest(BaseModel):
    post_id: int
