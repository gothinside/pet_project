from sqlalchemy.ext.asyncio import AsyncSession
from ..models import Service, Booking, client_booking, booking_service, Client
from sqlalchemy import select, insert, func, and_, update, delete
from ..schemas import BookingBase
from fastapi import HTTPException, status
from ..clients.utils import get_clients_by_user_id


async def _get_booking_by_id(db: AsyncSession, client_id: int) -> Booking|None:
    client = (await db.execute(
        select(Booking).where(Booking.id == client_id)
    )).scalar_one_or_none()
    return client

async def create_booking_data(db: AsyncSession, booking: BookingBase) -> int:
    new_booking = (await db.execute(
        insert(Booking).returning(Booking.id).values(**booking.model_dump())   
    )).scalar_one_or_none()
    await db.flush()
    return new_booking

async def create_client_booking(db: AsyncSession, client_id: int, booking_id: int):
    res = await db.execute(
        client_booking.insert().values(
            client_id = client_id,
            booking_id = booking_id
        )
    )
    await db.flush()

async def is_client_booking(db: AsyncSession, client_id: int, booking_id: int):
    res = (await db.execute(
        select(client_booking)
        .where(and_(client_booking.c.client_id == client_id),
                    client_booking.c.booking_id == booking_id)
    )).scalar_one_or_none()
    if res:
        return False
    return True

async def create_booking_service(db: AsyncSession, service_id: int, booking_id: int):
    await db.execute(
        booking_service.insert().values(
            booking_id = booking_id,
            service_id = service_id
        )
    )

async def get_clients_count_by_bookign_id(db: AsyncSession, booking_id):
    count = (await db.execute(
        select(client_booking)
        .where(booking_id == booking_id)
    )).scalars().all()
    return len(count)

async def get_clients_by_booking_id(db: AsyncSession, booking_id):
    clients = (await db.execute(
        select(Client)
        .join(Client.bookings)
        .where(Booking.id == booking_id)
    )).scalars().all()
    return clients

async def update_booking_data(db: AsyncSession, booking_id:int, booking: BookingBase) -> int:
    (await db.execute(
        update(Booking)
        .where(Booking.id == booking_id)
        .values(**booking.model_dump())   
    ))
    await db.flush()

async def delete_client_booking(db: AsyncSession, booking_id: int):
    (await db.execute(
        client_booking
        .delete()
        .where(client_booking.c.booking_id == booking_id)
    ))
    await db.flush()

async def delete_booking_service(db: AsyncSession, booking_id: int):
    await db.execute(
        booking_service
        .delete()
        .where(
            booking_service.c.booking_id == booking_id
        )
    )
    await db.flush()

async def get_service_booking_id(db: AsyncSession, booking_id: int):
    services = (await db.execute(
        select(Service)
        .where(Service.bookings)
        .where(Booking.id == booking_id)
    )).scalar_one_or_none()
    return services

async def get_booking_by_clients(db: AsyncSession, clients: list[int]):
    bookings = (await db.execute(
        select(Booking.id)
        .join(client_booking, client_booking.c.booking_id == Booking.id)
        .where(client_booking.c.client_id.in_(clients))
    )).scalars().all()
    return bookings

async def get_client_bookings_by_user_id(db: AsyncSession, user_id):
    clients = await get_clients_by_user_id(db, user_id)
    bookings = await get_booking_by_clients(db, clients)
    return bookings