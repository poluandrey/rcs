from uuid import uuid4

import aiofiles
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.orm import joinedload

from core.config import settings
from model.bot import RCSBot
from model.task import Task, TaskResult
from task.rcs import rcs_bulk_check


async def task_get(session: async_sessionmaker, limit, offset):
    async with session() as async_session:
        stmt = select(Task).limit(limit).offset(offset)
        async for row in await async_session.stream_scalars(stmt):
            yield row


async def task_create(session: async_sessionmaker, file, bot: RCSBot):
    uuid = str(uuid4())
    async with session() as async_session:
        task = Task(name=uuid)
        task.file = f'{file.filename}-{task.name}'
        async_session.add(task)
        await async_session.commit()
        await async_session.refresh(task)

    async with aiofiles.open(settings.STATIC_PATH.joinpath('tasks').joinpath(task.file), 'wb') as out_file:
        content = await file.read()
        await out_file.write(content)

    rcs_bulk_check.delay(task.id, task.file, bot.name)
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


async def get_task_result_file(session: async_sessionmaker, task_id: id):
    async with session() as async_session:
        task = await async_session.get(Task, task_id)

    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='task not found')

    return settings.STATIC_PATH.joinpath('tasks', 'results', f'{task.name}.xlsx')
