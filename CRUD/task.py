from uuid import uuid4

import aiofiles
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.orm import joinedload

from model.task import Task, TaskResult
from task.rcs import rcs_bulk_check


async def task_get(session: async_sessionmaker, limit, offset):
    async with session() as async_session:
        stmt = select(Task).limit(limit).offset(offset)
        async for row in await async_session.stream_scalars(stmt):
            yield row


async def task_create(session: async_sessionmaker, file):
    uuid = str(uuid4())
    async with session() as async_session:
        task = Task(name=uuid)
        task.file = f'{file.filename}-{task.name}'
        async_session.add(task)
        await async_session.commit()
        await async_session.refresh(task)

    async with aiofiles.open(task.file, 'wb') as out_file:
        content = await file.read()  # async read
        await out_file.write(content)  # async write

    rcs_bulk_check.delay(task.id, task.file)
    return task


async def task_countries(task_id, session: async_sessionmaker):
    async with session() as async_session:
        stmt = select(Task).where(Task.id == task_id)
        task = await async_session.scalar(stmt)
        if not task:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='task not found')

        stmt = select(TaskResult.country).where(TaskResult.task == task.id).distinct()
        countries = [country async for country in await async_session.stream_scalars(stmt)]

    return countries


async def task_capable_msisdns(session: async_sessionmaker, task_id: int, country: str, ):
    async with session() as async_session:
        stmt = select(Task).options(joinedload(Task.results)).where(Task.id == task_id)
        task = await async_session.scalar(stmt)
        if not task:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='task not found')

        msisdns = []
        task_results = task.results
        for result in task_results:
            if result.country == country:
                msisdns.append(result.msisdn)

    return msisdns
