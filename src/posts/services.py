import time
from src.posts.models import ReactionRequest, ReactionDB, PostReturn, FullPost
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, func, update, delete
from src.database.models import post, reactions
from sqlalchemy.exc import SQLAlchemyError


async def new_post(username: str, title: str, body: str, session: AsyncSession):
    new_post_stmt = (
        insert(post)
        .values(posted_username=username, title=title, body=body)
        .returning(post)
    )
    try:
        result = await session.execute(new_post_stmt)

        await session.commit()
        added_post = result.fetchone()
        return FullPost(
            id=added_post.id,
            posted_username=added_post.posted_username,
            posted_at=added_post.posted_at,
            title=added_post.title,
            body=added_post.body,
        )
    except SQLAlchemyError:
        return None


async def get_post_db(post_id: int, session: AsyncSession):
    post_stmt = select(post).where(post.c.id == post_id).limit(1)
    likes_stmt = select(func.count()).where(
        reactions.c.post_id == post_id, reactions.c.reaction == 1
    )
    dislikes_stmt = select(func.count()).where(
        reactions.c.post_id == post_id, reactions.c.reaction == -1
    )
    rez = 0
    try:
        result = await session.execute(post_stmt)
        result = result.fetchone()

        # if post not found
        if result is None:
            rez = 1
            return {"rez": rez, "post": None}

        likes = await session.execute(likes_stmt)
        likes = likes.fetchone()
        dislikes = await session.execute(dislikes_stmt)
        dislikes = dislikes.fetchone()

        post_data = FullPost(
            id=result.id,
            posted_username=result.posted_username,
            posted_at=result.posted_at,
            likes=likes[0],
            dislikes=dislikes[0],
            title=result.title,
            body=result.body,
        )
        rez = 2
        return {"rez": rez, "post": post_data}

    except Exception:
        return {"rez": rez, "post": None}


async def add_reaction_db(req: ReactionRequest, username: str, session: AsyncSession):
    react: int = 0
    if req.type == "Like":
        react = 1
    elif req.type == "Dislike":
        react = -1
    reaction = ReactionDB(
        reaction=react, reactkey=f"""{username}, {req.post_id}""", post_id=req.post_id
    )
    stmt = insert(reactions).values(**reaction.dict())
    try:
        await session.execute(stmt)
        await session.commit()
        return True
    except SQLAlchemyError:
        return False


async def edit_post(
    post_id: int, username: str, title: str, body: str, session: AsyncSession
):
    stmt = (
        update(post)
        .where(post.c.posted_username == username, post.c.id == post_id)
        .values(title=title, body=body)
    )
    try:
        rez = await session.execute(stmt)
        await session.commit()
        if rez.rowcount > 0:
            return 1  # Post edited
        else:
            return 2  # Post not found or access denied
    except SQLAlchemyError:
        return 3  # DataBase error
    pass


async def delete_post(post_id: int, username: str, session: AsyncSession):
    stmt = delete(post).where(post.c.posted_username == username, post.c.id == post_id)
    try:
        rez = await session.execute(stmt)
        await session.commit()
        if rez.rowcount > 0:
            return 1
        else:
            return 2
    except SQLAlchemyError:
        return 3

