from typing import Generator, Annotated

from sqlalchemy.orm import Session
from fastapi import Depends

from core.database import Base


def get_db() -> Generator:
    yield Base.db_session


SessionDep = Annotated[Session, Depends(get_db)]


def get_params(offset: int = 0, limit: int = 100):
    return {'offset': offset, 'limit': limit}

