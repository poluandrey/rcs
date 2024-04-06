import asyncio
from typing import List, Dict

from sqlalchemy import insert, select

from celery_app.app import celery_app
from RCS.client import ApiClient
from RCS.schema import RCSBatchCapabilityTask, RCSDataForCheck
from depends import get_db
from model.task import TaskResult, Task
from schema.task import BaseTaskResult
from utils.excell import ExcellReader


@celery_app.task()
def rcs_bulk_check(task_id) -> Dict:
    session = next(get_db())
    task = session.get(Task, task_id)
    reader = ExcellReader(task.file)
    data = reader.get_data_for_check()
    task_data = RCSBatchCapabilityTask(task_id=task_id, data=data)
    api_client = ApiClient()
    loop = asyncio.get_event_loop()
    results = loop.run_until_complete(make_request(api_client, task_data.data))
    task_results = []

    for country, coro_res in results.items():
        batch_request = coro_res.result()
        msisdns = batch_request.reachableUsers
        if msisdns:
            task_results.extend([BaseTaskResult(task=task_id, country=country, msisdn=msisdn) for msisdn in msisdns])
        else:
            task_results.append(BaseTaskResult(task=task_id, country=country, ))

    session.execute(insert(TaskResult), task_results)
    session.commit()


async def make_request(api_client: ApiClient, data_for_check: List[RCSDataForCheck]):
    results = {}
    async with asyncio.TaskGroup() as tg:
        for data in data_for_check:
            task = tg.create_task(api_client.batch_rcs_capable(data.msisdns))
            results[data.country] = task

    return results
