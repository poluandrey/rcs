import redis

from core.config import settings

client = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)
