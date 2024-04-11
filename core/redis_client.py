import redis

from core.config import settings

client = redis.Redis(host='localhost', port=6379)
