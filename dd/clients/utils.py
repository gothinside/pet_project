from enum import Enum
from sqlalchemy.ext.asyncio import AsyncSession
from ..models import Client, client_user, User
from ..schemas import ClientCreate
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import select
from fastapi import HTTPException

async def _get_client_by_id(db: AsyncSession, client_id: int) -> Client|None:
    client = (await db.execute(
        select(Client).where(Client.id == client_id)
    )).scalar_one_or_none()
    return client

async def _get_client_by_phone_numner(db: AsyncSession, phone_number: str):
    client = (await db.execute(
        select(Client).where(Client.phone_number == phone_number)
    )).scalar_one_or_none()
    return client

async def is_client_unique_by_id(db: AsyncSession, client_id: int) -> bool:
    if await _get_client_by_id(db, client_id):
        return False
    return True

async def is_client_unique_by_phone_number(db: AsyncSession, client_id: int) -> bool:
    if await _get_client_by_phone_numner(db, client_id):
        return False
    return True

async def create_client_user(db: AsyncSession, client_id: int, user_id: int) -> None:
    query = insert(client_user).values(client_id = client_id,
                                    user_id = user_id)
    query_do_nothing  = query.on_conflict_do_nothing(
    # index_elements=['id']
)
    await db.execute(
        query_do_nothing
    )
    # await db.flush()

async def create_client(db: AsyncSession, client: ClientCreate) -> int|None:
    if await is_client_unique_by_phone_number(db, client.phone_number):
        query = (
            insert(Client).returning(Client.id).values(**client.model_dump())
        )
        client_id = await db.execute(query)
        await db.flush()
        return client_id.scalar_one_or_none()
    return

async def get_clients_by_user_id(db: AsyncSession, user_id: int):
    clients = (await db.execute(
        select(Client.id)
        .join(Client.users)
        .where(User.id == user_id)
    )).scalars().all()
    return clients