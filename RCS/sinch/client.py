import httpx
from httpx import AsyncClient, Headers, codes

from core.config import settings
from RCS.sinch.schema import FailedCapabilityResponse, SuccessfulCapableResponse
from RCS.schema import RCSCapabilityResponse as ServiceCapabilityResponse


class ApiClient:

    def __init__(self, bot_id: str):
        self.bot_id = bot_id
        self.auth_header = Headers({'Authorization': f'Bearer {settings.SINCH_YOLLA_API_TOKEN}'})
        self.client = AsyncClient(headers=self.auth_header, base_url=settings.SINCH_BASE_ENDPOINT)

    async def rcs_capable(self, msisdn: str):
        params = {'msisdn': msisdn}
        resp = await self.client.get(url=f'{self.bot_id}/capabilities', params=params)

        is_capable = True if resp.status_code == codes.OK else False
        raw_resp = SuccessfulCapableResponse(**resp.json()) if resp.status_code == httpx.codes.OK \
            else FailedCapabilityResponse(**resp.json())

        return ServiceCapabilityResponse(rcs_enable=is_capable, raw_response=raw_resp)
