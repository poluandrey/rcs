import asyncio
from typing import List


from celery_app.app import celery_app
from core.database import AsyncSessionLocal
from model.task import TaskResult
from RCS.client import ApiClient
from RCS.schema import RCSBatchCapabilityTask, RCSDataForCheck
from utils.excell import ExcellReader


async def save_task_result(task_results):
    async with AsyncSessionLocal() as async_session:
        async_session.add_all(task_results)
        await async_session.commit()


@celery_app.task()
def rcs_bulk_check(task_id, task_file):
    reader = ExcellReader(task_file)
    data = reader.get_data_for_check()
    task_data = RCSBatchCapabilityTask(task_id=task_id, data=data)
    api_client = ApiClient()
    api_client.authenticate()
    loop = asyncio.get_event_loop()
    results = loop.run_until_complete(make_request(api_client, task_data.data))
    task_results = []

    for country, coro_res in results.items():
        batch_response = coro_res.result()
        msisdns = batch_response.reachableUsers
        if msisdns:
            task_results.extend([TaskResult(task=task_id, country=country, msisdn=msisdn) for msisdn in msisdns])
        else:
            task_results.append(TaskResult(task=task_id, country=country))

    loop.run_until_complete(save_task_result(task_results))


async def make_request(api_client: ApiClient, data_for_check: List[RCSDataForCheck]):
    results = {}
    async with asyncio.TaskGroup() as tg:
        for data in data_for_check:
            task = tg.create_task(api_client.batch_rcs_capable(data.msisdns))
            results[data.country] = task

    return results
