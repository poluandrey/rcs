from enum import Enum, auto
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import ENUM as PgEnum

from core.database import BaseModel
from RCS.google.client import ApiClient as GoogleApiClient
from RCS.sinch.client import ApiClient as SinchApiClient


class RCSBot(Enum):
    YollaGoogle = auto()
    YollaSinch = auto()


class Bot(BaseModel):
    __tablename__ = 'rcs_bot'

    bot = Column(PgEnum(RCSBot), unique=False, nullable=False)

    def get_api_client(self):
        match self.bot:
            case RCSBot.YollaGoogle:
                return GoogleApiClient()

            case RCSBot.YollaSinch:
                return SinchApiClient()
