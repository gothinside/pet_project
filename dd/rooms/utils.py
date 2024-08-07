from sqlalchemy.ext.asyncio import AsyncSession
from ..models import Room, Category
from sqlalchemy import select

async def _get_room_by_room_num(db: AsyncSession, room_num: int):
    room = (await db.execute(
        select(Room).where(Room.room_num == room_num)
    )).scalar_one_or_none()
    return room

async def is_room_unique_by_room_nuum(db: AsyncSession, room_num: int):
    room = await _get_room_by_room_num(db, room_num)
    if room:
        return False
    return True

async def get_beds_by_room_num(db: AsyncSession, room_num: int):
    beds = (await db.execute(
        select(Category.beds)
        .join(Room.category)
        .where(Room.room_num == room_num)  
    )).scalar_one_or_none()
    return beds