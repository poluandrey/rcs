from fastapi import APIRouter

from api.v1.endpoints.task import router as task_router
from api.v1.endpoints.auth import router as auth_router
from api.v1.endpoints.bot import router as bot_router

api_router = APIRouter(prefix='/v1', tags=['v1'])
api_router.include_router(task_router,)
api_router.include_router(auth_router,)
api_router.include_router(bot_router)
