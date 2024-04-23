from datetime import datetime, timedelta, timezone

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker

from jose import jwt
from starlette import status

from core.config import settings
from model.user import User


async def authenticate_user(session: async_sessionmaker, username: str, password: str):
    async with session() as async_session:
        stmt = select(User).where(User.username == username)
        user = await async_session.scalar(stmt)

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='user does not exists')

    if not user.verify_password(password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='incorrect password')

    return user


def create_access_token(data: dict):
    to_encode = data.copy()
    to_encode.update({'exp': datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt
