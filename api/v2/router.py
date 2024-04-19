from fastapi import APIRouter

from api.v2.endpoints.bot import router as bot_router


api_router = APIRouter(prefix='/v2', tags=['v2'])
api_router.include_router(bot_router)
