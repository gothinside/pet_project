from sqlalchemy.ext.asyncio import AsyncSession
from .. import models
from sqlalchemy import select, update

#only for using in this pacage
async def _get_category_by_name(db: AsyncSession, category_name: str):
    categories =  await db.execute(
        select(models.Category).where(models.Category.category_name == category_name)
    )
    categories = categories.scalar_one_or_none()
    return categories

async def _get_category_by_id(db: AsyncSession, category_id: int):
    categories =  await db.execute(
        select(models.Category).where(models.Category.id == category_id)
    )
    categories = categories.scalar_one_or_none()
    return categories

async def is_unique_by_category_name(db: AsyncSession, category_name):
    category = await _get_category_by_name(db, category_name)
    if category:
        return False
    return True