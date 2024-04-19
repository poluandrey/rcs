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

    async def batch_capability(self, phone_numbers: List[str]) -> List[str]:
        """return capable phone numbers"""
        capable_phone_numbers = []
        for phone_number in phone_numbers:
            if phone_number.startswith('+'):
                phone_number = phone_number.replace('+', '')
            resp = await self.client.rcs_capable(msisdn=phone_number)
            if resp.rcs_enable:
                capable_phone_numbers.append(phone_number)

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

