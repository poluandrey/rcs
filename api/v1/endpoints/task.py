from typing import List

from fastapi import APIRouter, UploadFile, Depends

from CRUD.task import task_get, task_create, task_countries, task_capable_msisdns, task_countries_test
from depends import SessionDep, get_params
from schema.task import BaseTask

router = APIRouter(prefix='/tasks')


@router.get(path='/', response_model=List[BaseTask])
async def get_tasks(session: SessionDep, params=Depends(get_params)):
    tasks = await task_get(session, **params)
    return tasks


@router.post(path='/', response_model=BaseTask)
async def create_task(session: SessionDep, file: UploadFile):
    task = await task_create(session, file)
    return task


@router.get(path='/{task_id}/country', response_model=List[str])
async def get_task_countries(session: SessionDep, task_id: int):
    countries = await task_countries(task_id, session)
    return countries


@router.get(path='/{task_id}/country/test', response_model=List[str])
async def get_task_countries(session: SessionDep, task_id: int):
    countries = await task_countries_test(task_id, session)
    return countries


@router.get(path='/{task_id}/{country}/')
async def get_capable_msisdn(session: SessionDep, task_id: int, country: str, ):
    msisdns = await task_capable_msisdns(session, task_id, country)
    return msisdns
