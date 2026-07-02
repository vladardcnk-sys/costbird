import json, redis.asyncio as aioredis
from core.config import Config

_redis = None

async def get_redis():
    global _redis
    if _redis is None:
        _redis = aioredis.from_url(Config.REDIS_URL, decode_responses=True)
    return _redis

async def cache_get(key: str):
    try:
        r = await get_redis()
        raw = await r.get(key)
        return json.loads(raw) if raw else None
    except Exception:
        return None

async def cache_set(key: str, value: dict):
    try:
        r = await get_redis()
        await r.setex(key, Config.CACHE_TTL, json.dumps(value, ensure_ascii=False))
    except Exception:
        pass
