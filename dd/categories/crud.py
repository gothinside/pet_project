from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from .. import models, schemas
from ..models import Category
from sqlalchemy import select, update, insert
from .utils import _get_category_by_id, _get_category_by_name
from .utils import *

async def get_cateogry_by_id(db: AsyncSession, category_id: int):
    category = await _get_category_by_id(db, category_id)
    if not category:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, 
            "category not found")
    return category


async def get_categories(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(
        select(models.Category).offset(skip).limit(limit)
    )
    return result.scalars().all()

async def create_category(db: AsyncSession, category: schemas.CategoryCreate):
    if not await is_unique_by_category_name(db, category.category_name):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Category name must be unique")

    new_category = Category(**category.model_dump())
    db.add(new_category)
    try:
        await db.commit()
        await db.refresh(new_category)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
    
    return new_category

async def update_category(db: AsyncSession, category_id: int, updated_category: schemas.CategoryUpdate):
    category = {key: value for key, value in updated_category.model_dump().items() if value != None}
    if category == {}:
       raise HTTPException(status.HTTP_400_BAD_REQUEST,
                            detail="You should change one field at least") 
    existing_category = await db.execute(
        select(models.Category).filter(models.Category.id == category_id)
    )
    category_by_id = existing_category.scalars().one_or_none()
    
    if not category_by_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    
    category = {key: value for key, value in updated_category.model_dump().items() if value != None}
    if not await is_unique_by_category_name(db, updated_category.category_name):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail="Category name must be unique")


    await db.execute(
        update(Category).
        where(Category.id == category_id).
        values(category)
    )
    
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
    
    return category

async def delete_category(db: AsyncSession, category_id: int):
    category = await get_cateogry_by_id(db,  category_id)
    
    try:
        await db.delete(category)
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
    
    return {"message": "Category deleted successfully"}
