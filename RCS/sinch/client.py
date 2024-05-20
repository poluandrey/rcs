import asyncio
import logging
from typing import AsyncIterator, List

from aiohttp import ClientSession, TCPConnector, ClientTimeout

from core.config import settings
from RCS.schema import RCSCapabilityResponse as ServiceCapabilityResponse
from RCS.sinch.schema import (FailedCapabilityResponse,
                              SuccessfulCapableResponse)

logging.getLogger('asyncio').setLevel(logging.WARNING)

BATCH_SIZE = 1000


class ApiClient:

    def __init__(self, bot_id: str):
        self.bot_id = bot_id
        self.session: ClientSession = ClientSession(
            base_url=settings.SINCH_BASE_ENDPOINT,
            connector=TCPConnector(use_dns_cache=True, limit=0),
            timeout=ClientTimeout(total=None)
        )
        self.session.headers.extend({'Authorization': f'Bearer {settings.SINCH_YOLLA_API_TOKEN}'})

    async def rcs_capable(self, phone_number: str, country=None) -> ServiceCapabilityResponse:
        params = {'msisdn': phone_number}
        async with self.session.get(url=f'/rcs/v1/{self.bot_id}/capabilities', params=params, ssl=False) as resp:
            resp_json = await resp.json()
            is_capable = True if resp.status == 200 else False
            raw_resp = SuccessfulCapableResponse(**resp_json) if resp.status == 200 \
                else FailedCapabilityResponse(**resp_json)

            return ServiceCapabilityResponse(
                phone_number=phone_number,
                country=country,
                rcs_enable=is_capable,
                raw_response=raw_resp
            )

    async def batch_capable(self, phone_numbers, country) -> AsyncIterator[List[ServiceCapabilityResponse]]:
        all_data_for_check = [(phone, country) for phone in phone_numbers]
        batch_data = []
        batch_tasks = []
        flag = True
        while flag:
            # prepare batch of data
            while all_data_for_check:
                if len(batch_data) + len(batch_tasks) < BATCH_SIZE:
                    batch_data.append(all_data_for_check.pop())
                    continue
                break
            if batch_data:
                batch_tasks.extend(
                    [
                        asyncio.create_task(self.rcs_capable(phone_number=data[0], country=data[1])) for data in batch_data
                    ]
                )
            print('send new requests')
            done, pending = await asyncio.wait(batch_tasks, timeout=1)
            print(f'done: {len(done)} pending: {len(pending)}')
            if done:
                result = [task.result() for task in done]
                yield result
            if pending:
                batch_tasks = [task for task in pending]
            else:
                batch_tasks = []

            batch_data = []
            print(f'{len(all_data_for_check)} requests did not send, {len(batch_tasks)} tasks in batch_tasks')
            if not all_data_for_check and not batch_tasks:
                flag = False
