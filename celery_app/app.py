from celery.app import Celery

from core.config import settings

celery_app = Celery(broker=settings.REDIS_URL, backend=settings.REDIS_URL, include=['task.rcs'])
