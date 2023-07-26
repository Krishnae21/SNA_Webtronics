import time
from src.posts.models import ReactionRequest, ReactionDB, PostReturn, FullPost
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update
from src.database.models import post, user, reactions
from sqlalchemy.exc import SQLAlchemyError



async def new_post(username: str, title: str, body: str, session: AsyncSession):
    stmt = insert(post).values(posted_username=username, title=title, body=body).returning(post)
    try:
        result = await session.execute(stmt)
        await session.commit()

        res = result.fetchone()

        return res
    except SQLAlchemyError:
        return None


async def get_post_db(post_id: int, session: AsyncSession):
    stmt = select(post).where(post.c.id == post_id).limit(1)
    try:
        result = await session.execute(stmt)
        result = result.fetchone()
        print(result)
        FullPost()
        # return PostReturn
    except SQLAlchemyError:
        return None


async def add_reaction_db(req: ReactionRequest, username: str, session: AsyncSession):
    react: int = 0
    if req.type == "Like":
        react = 1
    elif req.type == "Dislike":
        react = -1
    reaction = ReactionDB(reaction=react, reactkey=f"""{username}, {req.post_id}""")
    stmt = insert(reactions).values(**reaction.dict())
    error_stmt = reactions.update().where(reactions.c.reactkey == f"""{username}, {req.post_id}""").values(reaction=-1)
    try:
        await session.execute(stmt)
        await session.commit()
        return True
    except SQLAlchemyError:
        return False


