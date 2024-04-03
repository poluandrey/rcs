from celery.app import Celery

from config.settings import settings


app = Celery(broker=settings.REDIS_URL, backend=settings.REDIS_URL, include=['RCS.task'])
