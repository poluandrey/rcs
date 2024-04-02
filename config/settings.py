from pathlib import Path

from pydantic_settings import BaseSettings
from pydantic import Extra

BASE_DIR = Path(__file__).resolve().parent.parent
print(BASE_DIR)

class Settings(BaseSettings):

    RBM_BASE_ENDPOINT: str
    PATH_TO_SERVICE_ACCOUNT: str
    AGENT_ID: str
    JWT_GRANT_TYPE: str

    class Config:
        case_sensitive = True
        env_file = f'{BASE_DIR}/.env'
        extra = Extra.allow


settings = Settings()
