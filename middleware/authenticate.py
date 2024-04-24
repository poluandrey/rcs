from jose import JWTError, jwt
from sqlalchemy import select
from starlette.authentication import AuthenticationBackend, AuthenticationError
from starlette.requests import Request
from starlette.responses import Response

from core.config import settings
from core.database import AsyncSessionLocal
from model.user import User


class JWTAuthMiddleware(AuthenticationBackend):
    """decode Authorization token and srt current_user param for request"""

    async def authenticate(
        self,
        request: Request,
    ) -> Response:
        if 'authorization' not in request.headers:
            return

        token = request.headers.get('Authorization').split(' ')[-1]

        try:
            auth = jwt.decode(token, settings.SECRET_KEY, algorithms=settings.ALGORITHM)
        except JWTError:
            raise AuthenticationError('invalid token')

        username: str = auth.get('sub')
        async with AsyncSessionLocal() as async_session:
            stmt = select(User).where(User.username == username)
            user = await async_session.scalar(stmt)

        return auth, user
