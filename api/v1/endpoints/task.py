from typing import List

from fastapi import APIRouter, Depends, UploadFile
from fastapi.responses import FileResponse

from core.auth import security_schema
from core.database import AsyncSession
from CRUD.task import (get_task_result_file, task_capable_msisdns,
                       task_countries, task_create, task_get)
from depends import get_params
from schema.task import BaseTask

router = APIRouter(prefix='/tasks', dependencies=[Depends(security_schema)])


@router.get(path='/', response_model=List[BaseTask])
async def get_tasks(session: AsyncSession, params=Depends(get_params)):
    tasks = [task async for task in task_get(session, **params)]
    return tasks


@router.post(path='/', response_model=BaseTask)
async def create_task(session: AsyncSession, file: UploadFile):
    task = await task_create(session, file)
    return task


@router.get(path='/{task_id}/country', response_model=List[str])
async def get_task_countries(session: AsyncSession, task_id: int):
    countries = await task_countries(task_id, session)
    return countries


@router.get(path='/{task_id}/{country}/', response_model=List[str])
async def get_capable_msisdn(session: AsyncSession, task_id: int, country: str, ):
    msisdns = await task_capable_msisdns(session, task_id, country)
    return msisdns


@router.get(path='/{task_id}/download',)
async def download_task_result_file(session: AsyncSession, task_id: int):
    file = await get_task_result_file(session, task_id)
    headers = {'Content-Disposition': 'attachment; filename="Book.xlsx"'}
    return FileResponse(path=file, headers=headers)
