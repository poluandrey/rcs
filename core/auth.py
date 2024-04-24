from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext

security_schema = OAuth2PasswordBearer(tokenUrl='/v1/token')
AuthRequiredDep = Annotated[str, Depends(security_schema)]

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
