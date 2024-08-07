from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from .. import models, schemas
from ..models import Room, Category
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select, update, insert, literal_column
from ..categories.crud import _get_category_by_id, get_cateogry_by_id
from .utils import _get_room_by_room_num, is_room_unique_by_room_nuum

async def get_rooms(db: AsyncSession, skip:int, limit: int):
    rooms = (await db.execute(
        select(Room.room_num, Category.category_name)
        .join(Room.category)
        .where(Room.is_active == True)
        .limit(limit)
        .offset(skip)
    )).all()
    res = [{"room_num": room_num, "category_name": category_name} for room_num, category_name in rooms]
    return res

async def get_room(db: AsyncSession, room_num: int):
    room = await _get_room_by_room_num(db, room_num)
    if room is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND,
                             "Room not found")
    return room

async def create_room(db: AsyncSession, room: schemas.RoomCreate):
    category = await get_cateogry_by_id(db, room.category_id)
    
    if await _get_room_by_room_num(db, room.room_num):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail="This room number is not unique")
    
    new_room = Room(**room.model_dump())
    db.add(new_room)
    try:
        await db.commit()
        await db.refresh(new_room)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
    
    return new_room

async def update_room(db: AsyncSession, 
                      room_num: int, 
                      updated_room: schemas.RoomUpdate):
    await get_room(db, room_num)
    room = {key: value for key, value in updated_room.model_dump().items() if value != None}
    if room == {}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    if not await is_room_unique_by_room_nuum(db, updated_room.room_num) and room_num !=  updated_room.room_num:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Room must be unique")

    if not await _get_category_by_id(db, updated_room.category_id) and updated_room.category_id is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    
    changed_room = (await db.execute(
        update(Room)
        .where(Room.room_num == room_num)
        .values(room)
        .returning(Room.room_num)
    )).scalar_one()
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
    return await get_room(db, changed_room)

async def delete_room(db: Session, room_num: int):
    room = await get_room(db, room_num)
    
    try:
        await db.delete(room)
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
    
    return {"message": "Room deleted successfully"}
