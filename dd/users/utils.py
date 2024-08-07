from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from dd.models import User, Role

# async def _get_user_by_email(db: AsyncSession, email: str) -> User|None:
#     user = (await db.execute(
#         select(User).where(User.email == email)
#     )).scalar_one_or_none()
#     return user

# async def _get_user_by_id(db: AsyncSession, user_id: int) -> User|None:
#     user = (await db.execute(
#         select(User).where(User.id == user_id)
#     )).scalar_one_or_none()
#     return user

async def is_user_unique_by_id(db: AsyncSession, 
                               user_id: int) -> bool:
    user = (await db.execute(
        select(User).where(User.id == user_id)
    )).scalar_one_or_none()
    if user:
        return False
    return True

async def is_user_unique_by_email(db: AsyncSession, 
                                  email: str) -> bool:
    user = (await db.execute(
        select(User).where(User.email == email)
    )).scalar_one_or_none()
    if user:
        return False
    return True

