from sqlalchemy.orm import Session
from sqlalchemy import select
from model.task import Task


async def task_get(session: Session, limit, offset):
    stmt = select(Task).limit(limit).offset(offset)
    tasks = session.scalars(stmt)
    return tasks


async def task_create(session):
    task = Task()
    session.add(task)
    session.commit()
    session.refresh(task)
    return task
