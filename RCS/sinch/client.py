import asyncio
import logging
from datetime import datetime
from typing import List, AsyncIterator

import httpx
from aiohttp import ClientSession

from core.config import settings
from RCS.sinch.schema import FailedCapabilityResponse, SuccessfulCapableResponse
from RCS.schema import RCSCapabilityResponse as ServiceCapabilityResponse

limits = httpx.Limits(max_keepalive_connections=5, max_connections=10000)

logging.getLogger('asyncio').setLevel(logging.WARNING)


class ApiClient:

    def __init__(self, bot_id: str, session):
        self.bot_id = bot_id
        self.auth_header = {'Authorization': f'Bearer {settings.SINCH_YOLLA_API_TOKEN}'}
        self.session: ClientSession = session
        self.session.headers.extend(self.auth_header)

    async def rcs_capable(self, msisdn: str, country='undefined') -> ServiceCapabilityResponse:
        params = {'msisdn': msisdn}
        async with self.session.get(url=f'/rcs/v1/{self.bot_id}/capabilities', params=params, ssl=False) as resp:
            resp_json = await resp.json()
            is_capable = True if resp.status == 200 else False
            raw_resp = SuccessfulCapableResponse(**resp_json) if resp.status == 200 \
                else FailedCapabilityResponse(**resp_json)

            return ServiceCapabilityResponse(
                msisdn=msisdn,
                rcs_enable=is_capable,
                country=country,
                raw_response=raw_resp
            )

    async def batch_capable(self, msisdns, country) -> AsyncIterator[List[ServiceCapabilityResponse]]:
        tasks = []
        for msisdn in msisdns:
            coro = self.rcs_capable(msisdn=msisdn, country=country)
            task = asyncio.create_task(coro)
            tasks.append(task)
            if len(tasks) % 1000 == 0:
                start_time = datetime.now()
                batch_resp = await asyncio.gather(*tasks)

                print(f'{country}: spend {datetime.now() - start_time} for {len(tasks)} request')
                yield batch_resp
                tasks = []
        if tasks:
            start_time = datetime.now()
            batch_resp = await asyncio.gather(*tasks)
            print(f'{country}: spend {datetime.now() - start_time} for {len(tasks)} request')
            yield batch_resp
