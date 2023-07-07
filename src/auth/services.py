import time

from passlib.hash import bcrypt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert
from src.database.models import user
from sqlalchemy.exc import SQLAlchemyError


# async def register_user(user: UserCreate):
async def check_user(username: str, email: str, session: AsyncSession):
    query = (
        select(user).where(user.c.username == username, user.c.email == email).limit(1)
    )
    result = await session.execute(query)
    result = result.fetchone()
    if result is not None:
        return True
    else:
        return False


async def register_user(
    email: str, username: str, password: str, session: AsyncSession
) -> bool:
    stmt = insert(user).values(
        email=email, username=username, password=bcrypt.hash(password)
    )
    try:
        await session.execute(stmt)
        await session.commit()
        return True
    except SQLAlchemyError:
        return False


async def auth_user(username: str, password: str, session: AsyncSession) -> bool:
    query = select(user).where(user.c.username == username).limit(1)
    try:
        result = await session.execute(query)
        result = result.fetchone()
        if result is not None and bcrypt.verify(password, result.password):
            return True
        else:
            return False
    except SQLAlchemyError:
        return False
