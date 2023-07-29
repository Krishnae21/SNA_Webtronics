from config import REDIS_PORT, REDIS_HOST
import aioredis
from aioredis.exceptions import RedisError
import asyncio
import json


redis = aioredis.from_url("redis://localhost", decode_responses=True)


async def main():
    await redis.set("my-key", "value")
    value = await redis.get("my-key")
    print(value)


async def set_post_cache(post_id: int, data: dict):
    try:
        await redis.set(post_id, json.dumps(data), 30)
        return True
    except RedisError:
        return False


async def get_post_cache(post_id: int):
    try:
        rez = await redis.get(post_id)
        if rez:
            return json.loads(rez)
    except RedisError:
        return False
