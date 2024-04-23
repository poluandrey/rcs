from typing import List, Protocol

from RCS.schema import RCSCapabilityResponse
from RCS.sinch.client import ApiClient as SinchApiClient
from RCS.google.client import ApiClient as GoogleApiClient
from core.config import settings
from model.bot import RCSBot


class BotClient(Protocol):

    def __init__(self, client: SinchApiClient | GoogleApiClient):
        self.client = client

    async def batch_capability(self, phone_numbers: List[str], country: str) -> List[RCSCapabilityResponse]:
        pass

    async def capability(self, phone_number: str) -> RCSCapabilityResponse:
        pass


class Client:

    def __init__(self, client: SinchApiClient | GoogleApiClient):
        self.client = client


class YollaSinchBot:

    def __init__(self, client: SinchApiClient):
        self.client = client

    async def batch_capability(self, phone_numbers: List[str], country: str) -> List[RCSCapabilityResponse]:
        """return capable phone numbers"""
        capable_phone_numbers = []
        phone_numbers = [phone.replace('+', '') if phone.startswith('+') else phone
                         for phone in phone_numbers]
        async for resp in self.client.batch_capable(phone_numbers=phone_numbers, country=country):
            capable_phone_numbers.extend(resp)

        return capable_phone_numbers

    async def capability(self, phone_number: str) -> RCSCapabilityResponse:
        try:
            capability = await self.client.rcs_capable(phone_number)
        finally:
            await self.client.session.close()

        return capability


class YollaGoogleBot:

    def __init__(self, client: GoogleApiClient):
        self.client = client
        self.client.authenticate()

    async def batch_capability(self, phone_numbers: List[str], country: str) -> List[RCSCapabilityResponse]:
        """return capable phone numbers"""
        resp = []
        batch_resp = await self.client.batch_capable(msisdns=phone_numbers)
        for phone_number in phone_numbers:
            if batch_resp.reachableUsers:
                if phone_number in batch_resp.reachableUsers:
                    resp.append(RCSCapabilityResponse(
                        phone_number=phone_number,
                        rcs_enable=True,
                        country=country,
                        raw_response=batch_resp))
            else:
                resp.append(RCSCapabilityResponse(
                    phone_number=phone_number,
                    rcs_enable=False,
                    country=country,
                    raw_response=batch_resp))

        return resp

    async def capability(self, phone_number: str) -> RCSCapabilityResponse:
        phone_number = phone_number if phone_number.startswith('+') else f'+{phone_number}'
        try:
            capability = await self.client.rcs_capable(phone_number)

        finally:
            await self.client.session.close()

        return capability


def get_bot_client(bot: RCSBot) -> BotClient:
    match bot:
        case bot.YollaGoogle:
            api_client = GoogleApiClient()
            bot_client = YollaGoogleBot(api_client)
        case bot.YollaSinch:
            api_client = SinchApiClient(
                bot_id=settings.SINCH_YOLLA_SENDER_ID,
            )
            bot_client = YollaSinchBot(api_client)
    return bot_client
