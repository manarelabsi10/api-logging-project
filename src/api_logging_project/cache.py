import json
import os

import redis
from fastapi.encoders import jsonable_encoder


ITEMS_CACHE_KEY = "items:all"
ITEMS_CACHE_TTL_SECONDS = 60

redis_client = redis.Redis.from_url(
    os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    decode_responses=True,
)


def get_cached_items():
    cached_items = redis_client.get(ITEMS_CACHE_KEY)
    if cached_items is None:
        return None

    return json.loads(cached_items)


def cache_items(items):
    serialized_items = json.dumps(jsonable_encoder(items))
    redis_client.set(
        ITEMS_CACHE_KEY,
        serialized_items,
        ex=ITEMS_CACHE_TTL_SECONDS,
    )


def invalidate_items_cache():
    redis_client.delete(ITEMS_CACHE_KEY)