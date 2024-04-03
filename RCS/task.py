import asyncio
from typing import List, Dict

from celery_app.app import app
from RCS.rcs import RCSBatchCapabilityTask, RCSDataForCheck
from RCS.client import ApiClient


@app.task()
def dummy(task_data: Dict) -> Dict:
    task_data = RCSBatchCapabilityTask(**task_data)
    task_id = task_data.task_id
    api_client = ApiClient()
    loop = asyncio.get_event_loop()
    results = loop.run_until_complete(make_request(api_client, task_data.data))
    check_result = {country: result.result().dict() for country, result in results.items()}
    return {task_id: check_result}


async def make_request(api_client: ApiClient, data_for_check: List[RCSDataForCheck]):
    results = {}
    async with asyncio.TaskGroup() as tg:
        for data in data_for_check:
            task = tg.create_task(api_client.batch_rcs_capable(data.msisdns))
            results[data.country] = task

    return results


