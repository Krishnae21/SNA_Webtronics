from fastapi import APIRouter, Depends, Header
from fastapi.responses import JSONResponse
from src.posts.models import Post, PostReturn, ReactionReturn, ReactionRequest
from src.posts.services import new_post, get_post_db, add_reaction_db
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.database import get_async_session
from src.auth.jwt_auth import JwtAuth

router = APIRouter(prefix="/post", tags=["Posts"])


@router.post("/new", response_model=PostReturn)
async def new(post: Post, authorization: str = Header(), session: AsyncSession = Depends(get_async_session)):
    token = JwtAuth.validate_access_token(authorization)
    if token["status"]:
        current_user = token["user"]
        result = await new_post(current_user, post.title, post.body, session)

        return JSONResponse(status_code=200, content=PostReturn(status="Success", data=result).dict())
    else:
        return JSONResponse(status_code=401, content=PostReturn().dict())


@router.get("/{post_id}", response_model=PostReturn)
async def get_post(post_id: int, session: AsyncSession = Depends(get_async_session)):
    post = await get_post_db(post_id, session)
    return JSONResponse(status_code=200, content=PostReturn(status="Success", data=post).dict())


@router.post("/reaction", response_model=ReactionReturn, description="type: Like or Dislike")
async def like_get(react: ReactionRequest, Authorization: str = Header(), session: AsyncSession = Depends(get_async_session)):
    token = JwtAuth.validate_access_token(Authorization)
    if token["status"]:
        if await add_reaction_db(react, username=token["user"], session=session):
            return JSONResponse(status_code=200, content=ReactionReturn(status="Success", type=react.type).dict())
        else:
            return JSONResponse(status_code=200, content=ReactionReturn(status="Error", type=react.type).dict())
    else:
        return JSONResponse(status_code=200, content=ReactionReturn(status="Error", type=react.type).dict())

