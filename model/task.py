from sqlalchemy import UUID, Column, ForeignKey, String
from sqlalchemy.orm import relationship

from core.database import BaseModel


class Task(BaseModel):
    __tablename__ = 'task'

    name = Column(UUID)
    file = Column(String(length=120))
    result_file = Column(String(length=120))

    results = relationship('TaskResult', back_populates='task')


class TaskResult(BaseModel):
    __tablename__ = 'task_result'

    task_id = Column(ForeignKey(column='task.id'))
    country = Column(String(length=120))
    msisdn = Column(String(length=20))

    task = relationship('Task', back_populates='results')
