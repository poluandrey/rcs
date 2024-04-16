from typing import Annotated
from passlib.context import CryptContext


from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends


security_schema = OAuth2PasswordBearer(tokenUrl='/v1/token')
AuthRequiredDep = Annotated[str, Depends(security_schema)]

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
