import asyncio
from time import mktime
import json
from datetime import datetime, timedelta
from typing import List, Optional
from dataclasses import dataclass
from httpx import Headers
import httpx
from google.oauth2 import service_account


CLIENT_SECRETS_FILE = '/Users/andrey/Documents/work/new_hlr_product_alarm/RCS/resources/gbc-lanck-telecom-9mpavsi-24bb560004b8.json'
SCOPES = ['https://www.googleapis.com/auth/rcsbusinessmessaging']
URL = 'https://rcsbusinessmessaging.googleapis.com/v1/phones/+79216503431/capabilities?requestId=uds1-2222-3333-4444&agentId=yolla_zrmumsii_agent'
_JWT_GRANT_TYPE = "urn:ietf:params:oauth:grant-type:jwt-bearer"


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
        with open('/Users/andrey/Documents/work/new_hlr_product_alarm/RCS/token.json', 'r') as f:
            token = json.load(f)

        if not token.get('access_token'):
            return None

        now = datetime.utcnow()
        if token['expired_at'] < mktime(now.utctimetuple()):
            return None

        return token['access_token']

    @classmethod
    def set_access_token_in_redis(cls, access_token: str, expires_in: int, token_type: str ) -> None:
        expired_at = datetime.utcnow() + timedelta(seconds=expires_in)

        with open('/Users/andrey/Documents/work/new_hlr_product_alarm/RCS/token.json', 'w') as f:
            token = {
                'access_token': access_token,
                'expired_at': mktime(expired_at.utctimetuple()),
                'type': token_type,
            }
            json.dump(token, f)


class ApiClient:
    authorize_url = 'https://oauth2.googleapis.com/token'

    def __init__(self):
        self.client = httpx.AsyncClient()

    async def rcs_capable(self, url):
        resp = await self.client.get(url=url)

        if resp.status_code == httpx.codes.UNAUTHORIZED:
            auth_client = CustomAuthentication(secret_file=CLIENT_SECRETS_FILE, scopes=SCOPES, access_token=None)
            auth_client.authenticate(self.client)

        resp = await self.client.get(url=url)

        return resp


class CustomAuthentication:
    authorize_url = 'https://oauth2.googleapis.com/token'

    def __init__(self, secret_file: str, scopes: List[str], access_token: Optional[str]):
        credentials = service_account.Credentials.from_service_account_file(secret_file)
        self.credentials = credentials.with_scopes(scopes)
        self.credentials.token = access_token
        self.auth_client = httpx.Client()

    def obtain_token(self):
        assertion = self.credentials._make_authorization_grant_assertion()
        url = f'{self.authorize_url}?grant_type={_JWT_GRANT_TYPE}&assertion={assertion.decode("utf-8")}'
        resp = self.auth_client.post(url)
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
    token = Token()
    auth_client = CustomAuthentication(secret_file=CLIENT_SECRETS_FILE, scopes=SCOPES, access_token=token.access_token)
    api_client = ApiClient()
    auth_client.authenticate(api_client.client)
    async with asyncio.TaskGroup() as tg:
        task1 = tg.create_task(api_client.rcs_capable(URL))
        task2 = tg.create_task(api_client.rcs_capable(URL))
        task3 = tg.create_task(api_client.rcs_capable(URL))
        task4 = tg.create_task(api_client.rcs_capable(URL))
        task5 = tg.create_task(api_client.rcs_capable(URL))
        task6 = tg.create_task(api_client.rcs_capable(URL))
        task7 = tg.create_task(api_client.rcs_capable(URL))
        task8 = tg.create_task(api_client.rcs_capable(URL))
    duration = datetime.now() - start_time
    print(task1.result())


if __name__ == '__main__':
    asyncio.run(main3())

