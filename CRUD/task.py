from sqlalchemy.orm import Session
from sqlalchemy import select
from model.task import Task
from task.rcs import rcs_bulk_check
from utils.excell import ExcellReader


async def task_get(session: Session, limit, offset):
    stmt = select(Task).limit(limit).offset(offset)
    tasks = session.scalars(stmt)
    return tasks


async def task_create(session, file):
    task = Task()
    session.add(task)
    session.commit()
    reader = ExcellReader(file.file)
    data = reader.get_data_for_check()
    rcs_bulk_check.delay(task.id, [data.dict() for data in data])
    session.refresh(task)
    return task
