from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from .. import schemas
from ..database import SessionLocal, engine
from ..models import Base, User
from . import crud
from ..database import get_db
from ..auth import get_current_user_from_token
from ..admin.utils import is_admin
from fastapi_cache.decorator import cache
import time


router = APIRouter(
    prefix="/rooms",
    tags=["rooms"]
)


@router.get("/")
@cache(expire=30)
async def read_rooms(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    return await crud.get_rooms(db, skip, limit)

@router.get("/{room_num}")
@cache(expire=30)
async def read_rooms(room_num:int, session: AsyncSession = Depends(get_db)):
    return await crud.get_room(session, room_num)

@router.post("/")
async def create_room(room: schemas.RoomCreate, 
                      session: AsyncSession = Depends(get_db),
                      cur_user:User = Depends(get_current_user_from_token)):
    if await is_admin(session, cur_user.id):
        return await crud.create_room(session, room)
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

@router.patch("/{room_num}")
async def update_room(room_num: int, 
                      updated_room: schemas.RoomUpdate, 
                      session: AsyncSession = Depends(get_db),
                      cur_user:User = Depends(get_current_user_from_token)):
    if await is_admin(session, cur_user.id):
        return await crud.update_room(session, room_num, updated_room)
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

@router.delete("/{room_num}")
async def delete_room(room_num: int, 
                      session: AsyncSession = Depends(get_db),
                      cur_user:User = Depends(get_current_user_from_token)):
    if await is_admin(session, cur_user.id):
        return await crud.delete_room(session, room_num)
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
