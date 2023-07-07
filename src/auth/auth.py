from fastapi import APIRouter, Depends, exception_handlers
from fastapi.responses import JSONResponse
import src.auth.services as services
from src.database.database import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from src.auth.models import SignUpSchema, Token, AuthSchema, AuthReturn
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from config import jwt_secret
from pydantic import BaseModel


router = APIRouter(prefix="/auth", tags=["Authorization"])
exception = exception_handlers


class Settings(BaseModel):
    authjwt_secret_key: str = jwt_secret


@AuthJWT.load_config
def get_config():
    return Settings()


@router.post("/sign_in", response_model=AuthReturn, operation_id="authorize")
async def sign_in(
    user: AuthSchema,
    authorize: AuthJWT = Depends(),
    session: AsyncSession = Depends(get_async_session),
):
    if await services.auth_user(user.username, user.password, session):
        access_token = authorize.create_access_token(subject=user.username, fresh=True)
        refresh_token = authorize.create_refresh_token(subject=user.username)
        token = Token(access_token=access_token, refresh_token=refresh_token)
        return JSONResponse(status_code=200, content=AuthReturn().correct(token))

    else:
        return JSONResponse(status_code=401, content=AuthReturn().incorrect())


@router.post("/sign_up", response_model=AuthReturn, operation_id="authorize")
async def sign_up(
    user: SignUpSchema,
    session: AsyncSession = Depends(get_async_session),
    authorize: AuthJWT = Depends(),
):
    if await services.check_user(
        username=user.username, email=user.email, session=session
    ):
        return JSONResponse(status_code=401, content={AuthReturn().registered()})
    else:
        if await services.register_user(
            email=user.email,
            username=user.username,
            password=user.password,
            session=session,
        ):
            access_token = authorize.create_access_token(
                subject=user.username, fresh=True
            )
            refresh_token = authorize.create_refresh_token(subject=user.username)
            token = Token(access_token=access_token, refresh_token=refresh_token)
            return JSONResponse(status_code=200, content=AuthReturn().correct(token))


@router.get("/refresh", response_model=AuthReturn, operation_id="authorize")
async def refresh(authorize: AuthJWT = Depends()):
    try:
        authorize.jwt_refresh_token_required()
        current_user = authorize.get_jwt_subject()
        access_token = authorize.create_access_token(subject=current_user)
        authorize = Token(access_token=access_token, refresh_token=None)
        return JSONResponse(
            status_code=200,
            content=AuthReturn().correct(authorize),
        )
    except AuthJWTException:
        return JSONResponse(status_code=401, content=AuthReturn().token_error())
