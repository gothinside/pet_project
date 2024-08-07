from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from fastapi import HTTPException, status
from .. import models, schemas
from ..models import Service
from sqlalchemy.exc import IntegrityError
from .utils import _get_service_by_id, _get_service_by_service_name,is_service_is_unique_by_service_name

async def get_services(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(models.Service)
                              .where(Service.is_active == True)
                              .offset(skip)
                              .limit(limit))
    return result.scalars().all()

async def get_service_by_id(db: AsyncSession, service_id: int):
    if service := await _get_service_by_id(db, service_id):
        if service.is_active == False:
            raise HTTPException(status.HTTP_400_BAD_REQUEST,
                        "Service is not acitve")
        return service
    raise HTTPException(status.HTTP_404_NOT_FOUND,
                        "Service not found")
    

async def create_service(db: AsyncSession, service: schemas.ServiceCreate):
    if not await is_service_is_unique_by_service_name(db, service.service_name):
        raise HTTPException(status.HTTP_400_BAD_REQUEST,
                            "Service name must be unique")
    new_service = models.Service(**service.model_dump())
    db.add(new_service)
    try:
        await db.commit()
        await db.refresh(new_service)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR,
                            "Server error"
        )

    return new_service

async def update_service(db: AsyncSession, service_id: int, updated_service: schemas.ServiceUpdate):
    service = await get_service_by_id(db, service_id)
    service = {key: value
                for key, value in updated_service.model_dump().items() if value is not None}
    
    if service  == {}:
        raise HTTPException(status.HTTP_400_BAD_REQUEST,
                            "Empty data")
    
    if await _get_service_by_service_name(db, updated_service.service_name) and updated_service.service_name is not None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST,
                            "Service name must be unique")
    await db.execute(
        update(Service)
        .where(Service.service_id == service_id)
        .values(**service)
    )
    
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR,
                            "Server error"
        )
    return service

async def delete_service(db: AsyncSession, service_id: int):
    service = await get_service_by_id(db, service_id)

    try:
        await db.delete(service)
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR,
                            "Server error"
        )
    return "Service deleted sucssfully"