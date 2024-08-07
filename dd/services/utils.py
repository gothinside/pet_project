from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from fastapi import HTTPException, status
from .. import models, schemas
from ..models import Service
from sqlalchemy.exc import IntegrityError

async def _get_service_by_id(db: AsyncSession, service_id: int):
    result = await db.execute(
        select(Service)
        .where(Service.service_id == service_id)
    )
    return result.scalars().one_or_none()

async def _get_service_by_service_name(db: AsyncSession, service_name: int):
    result = await db.execute(
        select(Service)
        .where(Service.service_name == service_name)
    )
    return result.scalar_one_or_none()

async def is_service_is_unique_by_service_name(db: AsyncSession, service_name: str):
    service = await _get_service_by_service_name(db, service_name)
    if service:
        return False
    return True

async def is_service_is_unique_by_id(db: AsyncSession, service_id: int):
    service = await _get_service_by_id(db, service_id)
    if service:
        return False
    return True