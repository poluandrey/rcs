from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from core.database import AsyncSession
from schema.auth import Token
from service.auth import authenticate_user, create_access_token

router = APIRouter(
    prefix='/token',
    tags=['authentication']
)


@router.post('/', response_model=Token)
async def token(session: AsyncSession, form_data=Depends(OAuth2PasswordRequestForm)):
    user = await authenticate_user(session, username=form_data.username, password=form_data.password)
    token = create_access_token(data={'sub': user.username})

    return Token(access_token=token, token_type='bearer')
