from enum import Enum
from sqlalchemy.ext.asyncio import AsyncSession
from ..models import User, Role
from sqlalchemy import select
from fastapi import APIRouter, Depends, HTTPException, status
from ..database import get_db
from ..schemas import UserUpdate, UserCreate, UserBase
from .crud import create_admin_user, add_role, ROLES, delete_users_role
from ..auth import get_current_user_from_token
from .utils import is_superuser, is_admin

router = APIRouter(
    prefix="/admin",
    tags=["admin"]
)

@router.post("/", response_model=UserBase)
async def create_admin(admin: UserCreate,
                       session: AsyncSession = Depends(get_db),
                       cur_user: User = Depends(get_current_user_from_token)):
    if await is_superuser(session, cur_user.id) or 1:
        return await create_admin_user(session,
                                    admin)
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

@router.patch("/add_role_for_user/{user_id}")
async def add_new_role_for_user(user_id: int,
                      role: ROLES,
                      session: AsyncSession = Depends(get_db),
                      cur_user: User = Depends(get_current_user_from_token)):
    if await is_superuser(session, cur_user.id) or 1:
        return await add_role(session, user_id, role)
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

@router.patch("/delete_users_role/{user_id}")
async def delete_role_for_user(user_id: int,
                      role: ROLES,
                      session: AsyncSession = Depends(get_db),
                      cur_user: User = Depends(get_current_user_from_token)):
    if await is_superuser(session, cur_user.id) or 1:
        return await delete_users_role(session, user_id, role)
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)