from typing import List, Optional

from fastapi import APIRouter, HTTPException, UploadFile, status

from bot import get_bot_client
from core.database import AsyncSession
from CRUD.bot import bot_get
from CRUD.task import task_create
from model.bot import RCSBot, RCSBotAction, get_bot_methods
from schema.bot import BotBase
from schema.task import BaseTask

router = APIRouter(prefix='/bot')


@router.get(path='', response_model=List[BotBase])
async def get_bot(session: AsyncSession):
    bots = await bot_get(session)
    return bots


@router.get(path='/{bot}/methods', response_model=List[RCSBotAction])
async def bot_methods(bot: RCSBot):
    return get_bot_methods(bot)


@router.post(path='{bot}/capability')
async def bot_capability(bot: RCSBot, phone_number: Optional[str] = None):
    if RCSBotAction.capability not in get_bot_methods(bot):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='action not implemented')

    bot_client = get_bot_client(bot)
    capability_resp = await bot_client.capability(phone_number=phone_number)
    return capability_resp


@router.post(path='{bot}/batchCapability', response_model=BaseTask)
async def bot_batch_capability(bot: RCSBot, file: UploadFile, session: AsyncSession):
    if RCSBotAction.batchCapability not in get_bot_methods(bot):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='action not implemented')

    task = await task_create(session, file, bot)
    return task
