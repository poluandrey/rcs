from pathlib import Path

from pydantic import Extra, PostgresDsn, computed_field
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    PROJECT_NAME: str
    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_PORT: int

    GOOGLE_RBM_BASE_ENDPOINT: str
    GOOGLE_PATH_TO_SERVICE_ACCOUNT: str
    GOOGLE_AGENT_ID: str
    GOOGLE_JWT_GRANT_TYPE: str
    GOOGLE_SCOPES: str

    SINCH_YOLLA_API_TOKEN: str
    SINCH_YOLLA_SENDER_ID: str
    SINCH_BASE_ENDPOINT: str

    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_URL: str

    STATIC_DIR: str
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    ALGORITHM: str

    @computed_field
    @property
    def STATIC_PATH(self) -> Path:
        return BASE_DIR.joinpath(self.STATIC_DIR)

    @computed_field
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:  # ignore
        return str(PostgresDsn.build(
            scheme='postgresql+asyncpg',
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_SERVER,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DB,
        ))

    class Config:
        case_sensitive = True
        env_file = f'{BASE_DIR}/.env'
        extra = Extra.allow


settings = Settings()
