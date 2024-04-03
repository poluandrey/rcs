from sqlalchemy import UUID, Column, func

from core.database import BaseModel


class Task(BaseModel):
    __tablename__ = 'task'

    name = Column(UUID, default=func.gen_random_uuid())
