"""Google api client"""
import json
from dataclasses import dataclass
from datetime import datetime, timedelta
from time import mktime
from typing import List, Optional
from uuid import uuid4

import httpx
from google.oauth2 import service_account
from aiohttp import ClientSession, TCPConnector

from core.config import settings
from core.redis_client import client as redis_client
from RCS.google.schema import SuccessfulCapabilityResponse, FailedCapabilityResponse, RCSBatchCapabilityResponse
from RCS.schema import RCSCapabilityResponse as ServiceCapabilityResponse


@dataclass
class AccessToken:
    access_token: str
    expired_at: datetime
    type: str

    def is_expired(self) -> bool:
        if self.expired_at > datetime.now():
            return False

        return True


class Token:

    def __init__(self):
        self.access_token = self.get_access_token_from_redis()

    def get_access_token_from_redis(self) -> Optional[str]:
        token = redis_client.get('access_token')
        if not token:
            return None

        token = json.loads(token)
        now = datetime.utcnow()
        if token['expired_at'] < mktime(now.utctimetuple()):
            return None

        return token['access_token']

    @classmethod
    def set_access_token_in_redis(cls, access_token: str, expires_in: int, token_type: str) -> None:
        expired_at = datetime.utcnow() + timedelta(seconds=expires_in)
        token = {
            'access_token': access_token,
            'expired_at': mktime(expired_at.utctimetuple()),
            'type': token_type,
        }
        redis_client.set('access_token', json.dumps(token))


class ApiClient:

    def __init__(self):
        self.session = ClientSession(
            base_url=settings.GOOGLE_RBM_BASE_ENDPOINT,
            connector=TCPConnector(verify_ssl=False, use_dns_cache=True)
        )
        self.agent_id = settings.GOOGLE_AGENT_ID

    async def rcs_capable(self, msisdn: str, country: str = 'undefined') -> ServiceCapabilityResponse:
        """
        Make RCS capable request for number
        :param country:
        :param msisdn: phone number in e.164 format
        :return: True if number is RCS capable, else False
        """
        uuid = str(uuid4())
        params = [('requestId', uuid), ('agentId', self.agent_id)]

        async with self.session.get(url=f'/v1/phones/{msisdn}/capabilities', params=params) as resp:
            resp_json = await resp.json()

            if resp.status == 401:
                auth_client = CustomAuthentication(access_token=None)
                auth_client.authenticate(self.session)
                resp_json = await resp.json()

        is_capable = True if resp.status == 200 else False
        raw_response = SuccessfulCapabilityResponse(**resp_json) if resp.status == 200 \
            else FailedCapabilityResponse(**resp_json)

        return ServiceCapabilityResponse(rcs_enable=is_capable,
                                         phone_number=msisdn,
                                         country=country,
                                         raw_response=raw_response)

    async def batch_capable(self, msisdns: List[str]) -> RCSBatchCapabilityResponse:
        """
        Gets the RCS-enabled phone numbers for a list of users.
        The returned payload contains a list of RCS-enabled phone numbers reachable by the RBM platform for the
        specified users. Only phone numbers that are RCS-enabled for a carrier the agent is launched on will be returned
        The returned payload also contains values that can be used to estimate the potential reach of a list of phone
        numbers regardless of the launch status of the agent.
        :param msisdns: List of phone numbers in e.164 format
        :param country: Country for which send capability requests
        :return: RCSBatchCapabilityResponse instance
        """
        body = {
            'users': msisdns,
            'agentId': self.agent_id,
        }
        async with self.session.post('/v1/users:batchGet', json=body) as resp:
            if resp.status == 401:
                auth_client = CustomAuthentication(access_token=None)
                auth_client.authenticate(self.session)

                async with self.session.post('/users:batchGet', json=body) as resp:
                    resp_data = await resp.json()
                    return RCSBatchCapabilityResponse(**resp_data)

            resp_data = await resp.json()
            print(resp_data)

            return RCSBatchCapabilityResponse(**resp_data)

    def authenticate(self):
        token = Token()
        auth_client = CustomAuthentication(access_token=token.access_token)
        auth_client.authenticate(self.session)


class CustomAuthentication:
    authorize_url = 'https://oauth2.googleapis.com/token'

    def __init__(self, access_token: Optional[str]):
        credentials = service_account.Credentials.from_service_account_file(settings.GOOGLE_PATH_TO_SERVICE_ACCOUNT)
        self.credentials = credentials.with_scopes([settings.GOOGLE_SCOPES])
        self.credentials.token = access_token
        self.auth_client = httpx.Client()
        self.jwt_grant_type = settings.GOOGLE_JWT_GRANT_TYPE

    def obtain_token(self):
        assertion = self.credentials._make_authorization_grant_assertion()
        url = f'{self.authorize_url}?grant_type={self.jwt_grant_type}&assertion={assertion.decode("utf-8")}'
        resp = self.auth_client.post(url)
        resp.raise_for_status()
        return resp.json()

    def authenticate(self, session: ClientSession):
        if self.credentials.valid:
            access_token = self.credentials.token

        else:
            token = self.obtain_token()
            Token.set_access_token_in_redis(
                access_token=token['access_token'],
                expires_in=token['expires_in'],
                token_type=token['token_type'],
            )
            access_token = token['access_token']

        session.headers.extend({'Authorization': f'Bearer {access_token}'})

        return access_token
