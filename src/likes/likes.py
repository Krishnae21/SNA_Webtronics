from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.database import get_async_session
from src.auth.jwt_auth import JwtAuth

