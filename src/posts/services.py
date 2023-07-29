from src.posts.models import ReactionRequest, ReactionDB, PostReturn, FullPost
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, func, update, delete
from src.database.models import post, reactions
from sqlalchemy.exc import SQLAlchemyError
import sqlalchemy.exc as Sql_exc
import src.cache.cache as cache


async def new_post(username: str, title: str, body: str, session: AsyncSession):
    new_post_stmt = (
        insert(post)
        .values(posted_username=username, title=title, body=body)
        .returning(post)
    )

    try:
        result = await session.execute(new_post_stmt)
        await session.commit()

        if result.rowcount > 0:
            added_post = result.fetchone()
            # Post added to base
            return FullPost(
                id=added_post.id,
                posted_username=added_post.posted_username,
                posted_at=added_post.posted_at,
                title=added_post.title,
                body=added_post.body,
            )

        # Post not found in result
        else:
            return None

    except SQLAlchemyError:
        # Database error
        return None


async def get_post_db(post_id: int, session: AsyncSession):
    post_stmt = select(post).where(post.c.id == post_id).limit(1)
    try:
        result = await session.execute(post_stmt)
        if result.rowcount > 0:
            result = result.fetchone()
            reacts = await get_reactions(post_id, session)

            post_data = FullPost(
                id=result.id,
                posted_username=result.posted_username,
                posted_at=result.posted_at,
                likes=reacts.get("likes"),
                dislikes=reacts.get("dislikes"),
                title=result.title,
                body=result.body,
            )
            # Good result
            return {"rez": 1, "post": post_data}

        else:
            # Post not found
            return {"rez": 2, "post": None}

    except Sql_exc.SQLAlchemyError:
        # Database error
        return {"rez": 0, "post": None}


async def get_reactions(post_id: int, session: AsyncSession):
    redis_data = await cache.get_post_cache(post_id)
    if redis_data:
        return redis_data
    else:
        likes_stmt = select(func.count()).where(
            reactions.c.post_id == post_id, reactions.c.reaction == 1
        )
        dislikes_stmt = select(func.count()).where(
            reactions.c.post_id == post_id, reactions.c.reaction == -1
        )
        try:
            likes = await session.execute(likes_stmt)
            likes = likes.fetchone()
            dislikes = await session.execute(dislikes_stmt)
            dislikes = dislikes.fetchone()

            react_data = {"likes": likes[0], "dislikes": dislikes[0]}
            await cache.set_post_cache(post_id, react_data)
            # Return good result
            return react_data

        except Sql_exc.SQLAlchemyError:
            # Database error
            return None


async def add_reaction_db(
    req: ReactionRequest, username: str, session: AsyncSession
) -> int:
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
        # Reaction added
        return 1

    except Sql_exc.IntegrityError:
        # Reaction is duplicate
        return 2

    except SQLAlchemyError:
        # Database error
        return 3


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
        if rez.rowcount > 0:
            await session.commit()
            # Post edited
            return 1

        else:
            # Post not found or access denied
            return 2

    except SQLAlchemyError:
        # DataBase error
        return 3


async def delete_post(post_id: int, username: str, session: AsyncSession):
    reactions_stmt = delete(reactions).where(reactions.c.post_id == post_id)
    post_stmt = delete(post).where(
        post.c.posted_username == username, post.c.id == post_id
    )
    try:
        await session.execute(reactions_stmt)
        rez = await session.execute(post_stmt)
        await session.commit()
        if rez.rowcount > 0:
            # Post deleted
            return 1

        else:
            # Post not found
            return 2

    except SQLAlchemyError:
        # Database error
        return 3
