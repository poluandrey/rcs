from httpx import AsyncClient, Headers, codes

from core.config import settings
from RCS.sinch.schema import RcsErrorResponse, RcsCapableResponse


class ApiClient:

    def __init__(self):
        self.auth_header = Headers({'Authorization': f'Bearer {settings.SINCH_YOLLA_API_TOKEN}'})
        self.client = AsyncClient(headers=self.auth_header, base_url=settings.SINCH_BASE_ENDPOINT)

    async def rcs_capable(self, msisdn: str, bot_id: str):
        params = {'msisdn': msisdn}
        resp = await self.client.get(url=f'{bot_id}/capabilities', params=params)

        if resp.status_code in [codes.NOT_FOUND, codes.INTERNAL_SERVER_ERROR]:
            return RcsErrorResponse(**resp.json())

        return RcsCapableResponse(**resp.json())
