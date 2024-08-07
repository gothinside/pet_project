from fastapi import APIRouter, Depends
from . import crud
from sqlalchemy.ext.asyncio import AsyncSession
from ..models import User
from ..schemas import UserCreate, UserBase, UserUpdate
from ..database import get_db
from ..auth import get_current_user_from_token
from ..admin.utils import is_admin, is_superuser
from fastapi import HTTPException, status
from .crud import *

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

@router.get("/{user_id}", response_model = UserBase)
async def get_user(user_id: int,
                   session: AsyncSession = Depends(get_db),
                   cur_user: User = Depends(get_current_user_from_token)):
    if cur_user.id == user_id:
        user = await get_user_by_id(session, user_id)
        return user
    elif await is_admin(session, cur_user.id) and not await is_admin(session, user_id):
        user = await get_user_by_id(session, user_id)
        return user
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

@router.post("/", response_model = UserBase)
async def create_new_user(user: UserCreate, 
                          session: AsyncSession = Depends(get_db)):
    new_user = await crud.create_user(session, user)
    return new_user

@router.patch("/{user_id}", response_model= UserBase)
async def update_user(user_id:int,
                      patched_user: UserUpdate,
                      session: AsyncSession = Depends(get_db),
                      cur_user: User = Depends(get_current_user_from_token)):
    
    if cur_user.id == user_id:
        updated_user = await crud.update_user(session, user_id, patched_user)
        return updated_user
    elif await is_admin(session, cur_user.id) and not await is_admin(session, user_id):
        updated_user = await crud.update_user(session, user_id, patched_user)
        return updated_user
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

@router.delete("/{user_id}")
async def delete_user(user_id:int,
                      session: AsyncSession = Depends(get_db),
                      cur_user = Depends(get_current_user_from_token)):
    if cur_user.id == user_id:
        user = await crud.delete_user(session, user_id)
        return user
    elif await is_admin(session, cur_user.id) and not await is_admin(session, user_id):
        user = await crud.delete_user(session, user_id)
        return user
    elif await is_superuser(session, cur_user.id) and not await is_superuser(session, user_id):
        user = await crud.delete_user(session, user_id)
        return user
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)