from sqlalchemy import Column, String

from core.auth import pwd_context
from core.database import BaseModel


class User(BaseModel):
    __tablename__ = 'user'
    username = Column(String(length=60), unique=True)
    userpassword = Column(String(length=120))

    def get_password_hash(self, password: str) -> str:
        return pwd_context.hash(password)

    def verify_password(self, plain_password: str) -> bool:
        return pwd_context.verify(plain_password, self.userpassword)
