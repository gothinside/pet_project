from enum import Enum
from sqlalchemy.ext.asyncio import AsyncSession
from ..models import User, Role
from sqlalchemy import select
from fastapi import HTTPException, status

class ROLES(str, Enum):
    ROLE_USER = "ROLE_USER"
    ROLE_ADMIN = "ROLE_ADMIN"
    ROLE_SUPERUSER = "ROLE_SUPERUSER"


async def is_admin(db: AsyncSession, user_id: int) -> bool:
    user = user = (await db.execute(
        select(User).where(User.id == user_id)
    )).scalar_one_or_none()
    if not user:
        return False
    roles =  (await db.execute(
        select(Role.role_name).join(User.roles).where(User.id == user.id)
    )).scalars().all()
    print(roles)
    if ROLES.ROLE_ADMIN in roles or ROLES.ROLE_SUPERUSER in roles:
        return True
    return False


async def is_superuser(db: AsyncSession, user_id: int) -> bool:
    user = (await db.execute(
        select(User).where(User.id == user_id)
    )).scalar_one_or_none()
    if not user:
        return False
    roles =  (await db.execute(
        select(Role.role_name).join(User.roles).where(User.id == user.id)
    )).scalars().all()
    if ROLES.ROLE_SUPERUSER in roles:
        return True
    return False

async def role_from_db(db: AsyncSession,
                        role: ROLES) -> Role|None:
    role_in_db = (await db.execute(
        select(Role).where(Role.role_name == role)
    )).scalar_one_or_none()
    return role_in_db
