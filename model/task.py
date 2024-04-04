from sqlalchemy import UUID, Column, func, ForeignKey, String
from sqlalchemy.orm import relationship

from core.database import BaseModel


class Task(BaseModel):
    __tablename__ = 'task'

    name = Column(UUID, default=func.gen_random_uuid())

    results = relationship('TaskResult')


class TaskResult(BaseModel):
    __tablename__ = 'task_result'

    task = Column(ForeignKey(column='task.id'))
    country = Column(String(length=120))
    msisdn = Column(String(length=20))

