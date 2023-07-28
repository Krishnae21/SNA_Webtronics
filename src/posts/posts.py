from fastapi import APIRouter, Depends, Header
from fastapi.responses import JSONResponse
import src.posts.models as post_models
import src.posts.services as post_services
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.database import get_async_session
from src.auth.jwt_auth import JwtAuth

router = APIRouter(prefix="/post", tags=["Posts"])


@router.post("/new", response_model=post_models.PostReturn)
async def new(
    post: post_models.Post,
    Authorization: str = Header(),
    session: AsyncSession = Depends(get_async_session),
):
    token = JwtAuth.validate_access_token(Authorization)
    if token["status"]:
        current_user = token["user"]
        result = await post_services.new_post(
            current_user, post.title, post.body, session
        )
        return JSONResponse(
            status_code=200,
            content=post_models.PostReturn(status="Success", data=result).dict(),
        )
    else:
        return JSONResponse(status_code=403, content=post_models.PostReturn().dict())


@router.get("/{post_id}", response_model=post_models.PostReturn)
async def get_post(post_id: int, session: AsyncSession = Depends(get_async_session)):
    post = await post_services.get_post_db(post_id, session)
    print(post.get("rez"))
    if post.get("rez") == 2:
        return JSONResponse(
            status_code=200,
            content=post_models.PostReturn(
                status="Success", data=post.get("post")
            ).dict(),
        )
    elif post.get("rez") == 1:
        return JSONResponse(
            status_code=404,
            content=post_models.PostReturn(
                status="Error", details="Post not found"
            ).dict(),
        )
    else:
        return JSONResponse(
            status_code=500,
            content=post_models.PostReturn(
                status="Error", details="Internal server error"
            ).dict(),
        )


@router.post(
    "/reaction",
    response_model=post_models.ReactionReturn,
    description="type: Like or Dislike",
)
async def like_get(
    react: post_models.ReactionRequest,
    Authorization: str = Header(),
    session: AsyncSession = Depends(get_async_session),
):
    token = JwtAuth.validate_access_token(Authorization)
    if token["status"]:
        if await post_services.add_reaction_db(
            react, username=token["user"], session=session
        ):
            return JSONResponse(
                status_code=200,
                content=post_models.ReactionReturn(
                    status="Success", type=react.type
                ).dict(),
            )
        else:
            return JSONResponse(
                status_code=200,
                content=post_models.ReactionReturn(
                    status="Error", type=react.type
                ).dict(),
            )
    else:
        return JSONResponse(
            status_code=403,
            content=post_models.ReactionReturn(status="Error", type=react.type).dict(),
        )


@router.post("/edit", response_model=post_models.Return)
async def edit(
    edit: post_models.EditRequest,
    Authorization: str = Header(),
    session: AsyncSession = Depends(get_async_session),
):
    token = JwtAuth.validate_access_token(Authorization)
    if token["status"]:
        rez = await post_services.edit_post(
            edit.post_id, token.get("user"), edit.title, edit.body, session
        )
        if rez == 1:
            return JSONResponse(
                status_code=200, content=post_models.Return(status="Success").dict()
            )
        elif rez == 2:
            return JSONResponse(
                status_code=400,
                content=post_models.Return(
                    status="Fail", details="Post not found or access denied"
                ).model_dump(),
            )
        else:
            return JSONResponse(
                status_code=500,
                content=post_models.Return(
                    status="Error", details="Internal server error"
                ).dict(),
            )

    else:
        return JSONResponse(
            status_code=403,
            content=post_models.Return(
                status="Error", details="You don't have permission to access"
            ).dict(),
        )
    pass


@router.post("/delete", response_model=post_models.Return)
async def delete(
    post_id: post_models.DeleteRequest,
    Authorization: str = Header(),
    session: AsyncSession = Depends(get_async_session),
):
    token = JwtAuth.validate_access_token(Authorization)
    if token["status"]:
        rez = await post_services.delete_post(
            post_id.post_id, token.get("user"), session
        )
        if rez == 1:
            return JSONResponse(
                status_code=200, content=post_models.Return(status="Success").dict()
            )
        elif rez == 2:
            return JSONResponse(
                status_code=400,
                content=post_models.Return(
                    status="Fail", details="Post not found or access denied"
                ).model_dump(),
            )
        else:
            return JSONResponse(
                status_code=500,
                content=post_models.Return(
                    status="Error", details="Internal server error"
                ).dict(),
            )
    else:
        return JSONResponse(
            status_code=403,
            content=post_models.Return(
                status="Error", details="You don't have permission to access"
            ).dict(),
        )
