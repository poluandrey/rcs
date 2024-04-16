from fastapi import FastAPI
from starlette.middleware.authentication import AuthenticationMiddleware

from api.v1.router import api_router
from core.config import settings
from middleware.authenticate import JWTAuthMiddleware

app = FastAPI(title=settings.PROJECT_NAME)
app.include_router(api_router)

app.add_middleware(AuthenticationMiddleware, backend=JWTAuthMiddleware())
