from typing import List

from fastapi import APIRouter, UploadFile, Depends

from CRUD.task import task_get, task_create
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
