import asyncio
import json
from dataclasses import dataclass
from datetime import datetime, timedelta
from time import mktime
from typing import List, Optional
from uuid import uuid4

import httpx
from google.oauth2 import service_account
from httpx import Headers

from config.settings import settings
from RCS.rcs import RCSBatchCapabilityResponse


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
        with open('../token.json', 'r') as f:
            token = json.load(f)

        if not token.get('access_token'):
            return None

        now = datetime.utcnow()
        if token['expired_at'] < mktime(now.utctimetuple()):
            return None

        return token['access_token']

    @classmethod
    def set_access_token_in_redis(cls, access_token: str, expires_in: int, token_type: str) -> None:
        expired_at = datetime.utcnow() + timedelta(seconds=expires_in)

        with open('../token.json', 'w') as f:
            token = {
                'access_token': access_token,
                'expired_at': mktime(expired_at.utctimetuple()),
                'type': token_type,
            }
            json.dump(token, f)


class ApiClient:

    def __init__(self):
        self.client = httpx.AsyncClient(base_url=settings.RBM_BASE_ENDPOINT)
        self.agent_id = settings.AGENT_ID
        self.authenticate()

    async def rcs_capable(self, msisdn: str) -> bool:
        """
        Make RCS capable request for number
        :param msisdn: phone number in e.164 format
        :return: True if number is RCS capable, else False
        """
        uuid = str(uuid4())

        params = [('requestId', uuid), ('agentId', self.agent_id)]
        resp = await self.client.get(url=f'/phones/{msisdn}/capabilities', params=params)

        if resp.status_code == httpx.codes.UNAUTHORIZED:
            auth_client = CustomAuthentication(access_token=None)
            auth_client.authenticate(self.client)
            resp = await self.client.get(url=f'/phones/{msisdn}/capabilities', params=params)

        return True if resp.status_code == httpx.codes.OK else False

    async def batch_rcs_capable(self, msisdns: List[str]) -> RCSBatchCapabilityResponse:
        """
        Gets the RCS-enabled phone numbers for a list of users.
        The returned payload contains a list of RCS-enabled phone numbers reachable by the RBM platform for the
        specified users. Only phone numbers that are RCS-enabled for a carrier the agent is launched on will be returned
        The returned payload also contains values that can be used to estimate the potential reach of a list of phone
        numbers regardless of the launch status of the agent.
        :param msisdns: List of phone numbers in e.164 format
        :return: RCSBatchCapabilityResponse instance
        """
        body = {
            'users': msisdns,
            'agentId': self.agent_id,
        }
        resp = await self.client.post('/users:batchGet', json=body)
        if resp.status_code == httpx.codes.UNAUTHORIZED:
            auth_client = CustomAuthentication(access_token=None)
            auth_client.authenticate(self.client)
            resp = await self.client.post('/users:batchGet', json=body)

        resp_data = resp.json()
        print(resp_data)
        batch_resp = RCSBatchCapabilityResponse(**resp_data)

        return batch_resp

    def authenticate(self):
        token = Token()
        auth_client = CustomAuthentication(access_token=token.access_token)
        auth_client.authenticate(self.client)


class CustomAuthentication:
    authorize_url = 'https://oauth2.googleapis.com/token'

    def __init__(self, access_token: Optional[str]):
        credentials = service_account.Credentials.from_service_account_file(settings.PATH_TO_SERVICE_ACCOUNT)
        self.credentials = credentials.with_scopes([settings.SCOPES])
        self.credentials.token = access_token
        self.auth_client = httpx.Client()
        self.jwt_grant_type = settings.JWT_GRANT_TYPE

    def obtain_token(self):
        assertion = self.credentials._make_authorization_grant_assertion()
        url = f'{self.authorize_url}?grant_type={self.jwt_grant_type}&assertion={assertion.decode("utf-8")}'
        print(url)
        resp = self.auth_client.post(url)
        print(resp.json())
        resp.raise_for_status()
        return resp.json()

    def authenticate(self, client: httpx.AsyncClient):
        if self.credentials.valid:
            print('use token from redis')
            access_token = self.credentials.token

        else:
            print('obtain token')
            token = self.obtain_token()
            Token.set_access_token_in_redis(
                access_token=token['access_token'],
                expires_in=token['expires_in'],
                token_type=token['token_type'],
            )
            access_token = token['access_token']
        client.headers = Headers({'Authorization': f'Bearer {access_token}'})

        return access_token


async def main3():
    start_time = datetime.now()
    # token = Token()
    # auth_client = CustomAuthentication(access_token=token.access_token)
    api_client = ApiClient()
    # auth_client.authenticate(api_client.client)
    async with asyncio.TaskGroup() as tg:
        task1 = tg.create_task(api_client.batch_rcs_capable(msisdns=['+447359388306']), name='uk')
        task2 = tg.create_task(api_client.rcs_capable(msisdn='+79216503431'))
        # task3 = tg.create_task(api_client.rcs_capable(URL))
        # task4 = tg.create_task(api_client.rcs_capable(URL))
        # task5 = tg.create_task(api_client.rcs_capable(URL))
        # task6 = tg.create_task(api_client.rcs_capable(URL))
        # task7 = tg.create_task(api_client.rcs_capable(URL))
        # task8 = tg.create_task(api_client.rcs_capable(URL))
    duration = datetime.now() - start_time
    print(task1.result(), task1.get_name(), task2.result())
    print(duration)


if __name__ == '__main__':
    asyncio.run(main3())