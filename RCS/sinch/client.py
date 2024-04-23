import asyncio
import logging
from datetime import datetime
from typing import List, AsyncIterator

from aiohttp import ClientSession, TCPConnector

from core.config import settings
from RCS.sinch.schema import FailedCapabilityResponse, SuccessfulCapableResponse
from RCS.schema import RCSCapabilityResponse as ServiceCapabilityResponse

logging.getLogger('asyncio').setLevel(logging.WARNING)

BATCH_SIZE = 1000


class ApiClient:

    def __init__(self, bot_id: str):
        self.bot_id = bot_id
        self.session: ClientSession = ClientSession(
            base_url=settings.SINCH_BASE_ENDPOINT,
            connector=TCPConnector(verify_ssl=False, use_dns_cache=True)
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
        phones_batch = [phone_numbers[i:i + BATCH_SIZE] for i in range(0, len(phone_numbers), BATCH_SIZE)]
        for batch in phones_batch:
            tasks = [asyncio.create_task(self.rcs_capable(phone_number=phone, country=country)) for phone in batch]
            start_time = datetime.now()
            batch_resp = await asyncio.gather(*tasks)
            print(f'{country}: spend {datetime.now() - start_time} for {len(tasks)} requests', flush=True)
            yield batch_resp
