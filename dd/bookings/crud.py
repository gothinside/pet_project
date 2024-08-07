from sqlalchemy.ext.asyncio import AsyncSession
from ..models import User, Role, Booking, client_user
from sqlalchemy import select, update
from fastapi import HTTPException, status
from ..schemas import BookingCreate, ClientCreate, BookingUpdate
from sqlalchemy.exc import IntegrityError
from ..rooms.utils import get_beds_by_room_num
from ..rooms.crud import get_room
from ..services.crud import get_service_by_id
from ..services.utils import is_service_is_unique_by_id
from ..clients.utils import (
    create_client, create_client_user, 
    _get_client_by_phone_numner, get_clients_by_user_id)
from .utils import *
from .utils import _get_booking_by_id

async def get_booking_by_id(db: AsyncSession, id: int) -> Booking:
    #Можно и одним запросом
    booking = await _get_booking_by_id(db, id)
    clients = await get_clients_by_booking_id(db, id)
    services = await get_service_booking_id(db, id)
    if not booking:
        raise HTTPException(status.HTTP_404_NOT_FOUND,
                            "Booking not found")
    if services is not None:
        return [booking, clients, services]
    return [booking, clients]

async def get_clients_bookings(db: AsyncSession, user_id: int):
    bookings = await get_client_bookings_by_user_id(db, user_id)
    return [await get_booking_by_id(db, booking) for booking in bookings]

async def get_clients_booking(db: AsyncSession, booking_id: int, user_id: int):
    bookings = await get_client_bookings_by_user_id(db, user_id)
    if booking_id in bookings:
        return await get_booking_by_id(db, booking_id)
    return HTTPException(status.HTTP_403_FORBIDDEN)

async def create_booking(db: AsyncSession, booking: BookingCreate, user_id: int):
    room = await get_room(db, booking.booking_data.room_num)
    beds = await get_beds_by_room_num(db, room.room_num)
    if beds < len(booking.clients):
        raise HTTPException(status.HTTP_400_BAD_REQUEST,
                             "Beds should be more then clients or equal")
    booking_id  = await create_booking_data(db, booking.booking_data)
    for client in booking.clients:
        client_from_db = await _get_client_by_phone_numner(db, client.phone_number)
        if client_from_db is None:
            client_id = await create_client(db, client)
            await create_client_booking(db, client_id, booking_id)
            await create_client_user(db, client_id, user_id)
        else:
            client_id = client_from_db.id
            await create_client_booking(db, client_id, booking_id)
            await create_client_user(db, client_id, user_id)

    for service_id in booking.services_ids:
        await get_service_by_id(db, service_id)
        await create_booking_service(db, service_id, booking_id)

    await db.commit()

    booking_data = await get_booking_by_id(db, booking_id)
    return booking_data

        
async def delete_booking_by_id(db: AsyncSession, booking_id: int) -> dict:
    booking = await _get_booking_by_id(db, booking_id)
    try:
        await db.delete(booking)
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR,
                            "Server error"
        )
    return {"message: Booking deleted"}

async def update_booking(db: AsyncSession,
                         booking_id: int,
                         patched_data: BookingCreate):
    await get_booking_by_id(db ,booking_id)

    updated_data = { key : value 
                    if key != "room_num"
                    else (await get_room(db, value)).room_num
                    for key,value in patched_data.model_dump().items()
                    if value is not None}

    if patched_data.room_num is not None:
        count = await get_clients_count_by_bookign_id(db, booking_id)
        if count > await get_beds_by_room_num(db, patched_data.room_num):
            raise HTTPException(400)
    
    if updated_data == {}:
        raise HTTPException(status.HTTP_400_BAD_REQUEST,
                            detail="You should change one field at least")
    
    await  db.execute(
        update(Booking)
        .where(Booking.id == booking_id)
        .values(**updated_data)
    )
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR,
                            "Server error"
        )
    return {"message: Booking updated"}

async def put_booking(db: AsyncSession,
                         user_id: int, 
                         booking_id: int,
                         booking: BookingCreate):
    await get_booking_by_id(db ,booking_id)
    room = await get_room(db, booking.booking_data.room_num)
    beds = await get_beds_by_room_num(db, room.room_num)
    if beds < len(booking.clients):
        raise HTTPException(status.HTTP_400_BAD_REQUEST,
                             "Beds should be more then clients or equal")
    await update_booking_data(db, booking_id, booking.booking_data)
    await delete_client_booking(db, booking_id)
    for client in booking.clients:
        client_from_db = await _get_client_by_phone_numner(db, client.phone_number)
        if client_from_db is None:
            client_id = await create_client(db, client)
            await create_client_booking(db, client_id, booking_id)
            await create_client_user(db, client_id, user_id)
        else:
                client_id = client_from_db.id
                await create_client_booking(db, client_id, booking_id)
    await delete_booking_service(db, booking_id)
    for service_id in booking.services_ids:
        await get_service_by_id(db, service_id)
        await create_booking_service(db, service_id, booking_id)

    await db.commit()
    return await get_booking_by_id(db, booking_id)