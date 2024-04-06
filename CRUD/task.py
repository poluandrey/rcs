import aiofiles

from sqlalchemy.orm import Session
from sqlalchemy import select
from fastapi import HTTPException, status

from model.task import Task, TaskResult
from task.rcs import rcs_bulk_check


async def task_get(session: Session, limit, offset):
    stmt = select(Task).limit(limit).offset(offset)
    tasks = session.scalars(stmt)
    return tasks


async def task_create(session, file):
    task = Task()
    session.add(task)
    session.commit()
    task.file = f'/Users/andrey/Documents/work/new_hlr_product_alarm/RCS/static/tasks/{file.filename}-{task.name}'
    session.commit()
    async with aiofiles.open(task.file, 'wb') as out_file:
        content = await file.read()  # async read
        await out_file.write(content)  # async write
    rcs_bulk_check.delay(task.id)
    session.refresh(task)
    return task


async def task_countries(task_id, session):
    stmt = select(Task).where(Task.id == task_id)
    task = session.scalar(stmt)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='task not found')

    stmt = select(TaskResult.country).where(TaskResult.task == task.id).distinct()
    countries = session.scalars(stmt)
    return countries


async def task_countries_test(task_id, session):
    stmt = select(Task).where(Task.id == task_id)
    task = session.scalar(stmt)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='task not found')

    results = task.results
    countries = set(result.country for result in results)
    return countries


async def task_capable_msisdns(session, task_id: int, country: str, ):
    stmt = select(Task).where(Task.id == task_id)
    task = session.scalar(stmt)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='task not found')
    msisdns = []
    task_results = task.results
    for result in task_results:
        if result.country == country:
            msisdns.append(result.msisdn)

    return msisdns

