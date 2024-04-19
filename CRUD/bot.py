from sqlalchemy import select

from model.rcs import Bot


async def bot_get(session):
    async with session() as async_session:
        stmt = select(Bot)
        bots = await async_session.scalars(stmt)
    return bots
