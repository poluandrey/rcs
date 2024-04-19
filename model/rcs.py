from enum import Enum
from typing import List

from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import ENUM as PgEnum

from core.database import BaseModel


class RCSBot(Enum):
    YollaGoogle = 'YollaGoogle'
    YollaSinch = 'YollaSinch'


class RCSBotAction(Enum):
    capability = 'capability'
    batchCapability = 'batchCapability'


def get_bot_methods(bot: RCSBot) -> List[RCSBotAction]:
    match bot:
        case bot.YollaSinch:
            return [RCSBotAction.capability, RCSBotAction.batchCapability]
        case bot.YollaGoogle:
            return [RCSBotAction.capability, RCSBotAction.batchCapability]


class Bot(BaseModel):
    __tablename__ = 'rcs_bot'

    bot = Column(PgEnum(RCSBot), unique=False, nullable=False)
