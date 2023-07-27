from fastapi import APIRouter, Depends, Header
from fastapi.responses import JSONResponse
import src.auth.services as services
from src.database.database import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from src.auth.models import SignUpSchema, Token, AuthSchema, AuthReturn
from pydantic import BaseModel
from src.auth.jwt_auth import JwtAuth
from datetime import timedelta


router = APIRouter(prefix="/auth", tags=["Authorization"])


@router.post("/sign_in", response_model=AuthReturn)
async def sign_in(
    user: AuthSchema,
    session: AsyncSession = Depends(get_async_session),
):
    if await services.auth_user(user.username, user.password, session):
        access_token = JwtAuth.create_token(user.username)
        refresh_token = JwtAuth.create_token(
            user.username, type_token="refresh", expire=timedelta(days=7)
        )
        token = Token(access_token=access_token, refresh_token=refresh_token)
        return JSONResponse(status_code=200, content=AuthReturn().correct(token))

    else:
        return JSONResponse(status_code=401, content=AuthReturn().incorrect())


@router.post("/sign_up", response_model=AuthReturn)
async def sign_up(
    user: SignUpSchema,
    session: AsyncSession = Depends(get_async_session),
):
    if await services.check_user(
        username=user.username, email=user.email, session=session
    ):
        return JSONResponse(status_code=401, content=AuthReturn().registered())
    else:
        if await services.register_user(
            email=user.email,
            username=user.username,
            password=user.password,
            session=session,
        ):
            access_token = JwtAuth.create_token(user.username)
            refresh_token = JwtAuth.create_token(
                user.username, type_token="refresh", expire=timedelta(days=7)
            )
            token = Token(access_token=access_token, refresh_token=refresh_token)
            return JSONResponse(status_code=200, content=AuthReturn().correct(token))
    return JSONResponse(status_code=500, content="Internal Server Error")


@router.get("/refresh", response_model=AuthReturn)
async def refresh(authorization: str = Header()):
    token = JwtAuth.refresh_token(authorization)
    if token["status"]:
        response = Token(access_token=token["token"], refresh_token=None)
        return JSONResponse(
            status_code=200,
            content=AuthReturn().correct(response),
        )
    else:
        return JSONResponse(status_code=401, content=AuthReturn().token_error())
