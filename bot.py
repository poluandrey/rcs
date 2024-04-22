from typing import List

from RCS.schema import RCSCapabilityResponse
from RCS.sinch.client import ApiClient as SinchApiClient
from RCS.google.client import ApiClient as GoogleApiClient


class RCSBotClient:

    def __init__(self, client: SinchApiClient | GoogleApiClient):
        self.client = client


class YollaSinchBot(RCSBotClient):

    def __init__(self, client: SinchApiClient):
        super().__init__(client)

    async def batch_capability(self, phone_numbers: List[str], country: str) -> List[RCSCapabilityResponse]:
        """return capable phone numbers"""
        capable_phone_numbers = []
        phone_numbers = [phone.replace('+', '') if phone.startswith('+') else phone
                         for phone in phone_numbers
                         ]
        async for resp in self.client.batch_capable(msisdns=phone_numbers, country=country):
            capable_phone_numbers.extend(resp)

        return capable_phone_numbers

    async def capability(self, phone_number: str) -> RCSCapabilityResponse:
        capability = await self.client.rcs_capable(phone_number)
        return capability


class YollaGoogleBot(RCSBotClient):

    def __init__(self, client: GoogleApiClient):
        super().__init__(client)
        self.client.authenticate()

    async def batch_capability(self, phone_numbers: List[str]) -> List[str]:
        """return capable phone numbers"""
        resp = await self.client.batch_capable(msisdns=phone_numbers)
        return resp.reachableUsers

    async def capability(self, phone_number: str) -> RCSCapabilityResponse:
        capability = await self.client.rcs_capable(phone_number)
        return capability
