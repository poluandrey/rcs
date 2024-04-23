from pydantic import BaseModel

from model.bot import RCSBot
# from RCS.google.schema import


class BotBase(BaseModel):
    id: int
    bot: RCSBot

    class Config:
        orm_model = True
        from_attributes = True
