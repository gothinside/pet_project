from sqlalchemy.ext.asyncio import AsyncSession
from ..models import User, Role
from sqlalchemy import select
from fastapi import APIRouter, Depends, HTTPException, status
from ..schemas import Booking, BookingCreate
from .crud import *
from ..database import get_db
from ..auth import get_current_user_from_token
from ..admin.utils import is_admin

router = APIRouter(
    prefix="/bookings",
    tags=["bookings"]
)
@router.get("/{booking_id}")
async def get_booking(booking_id: int, 
                      session = Depends(get_db),
                      cur_user = Depends(get_current_user_from_token)):
    bookings = await get_client_bookings_by_user_id(session, cur_user.id)
    if booking_id in bookings:
        return await get_booking_by_id(session, booking_id)
    elif await is_admin(session, cur_user.id):
        return await get_booking_by_id(session, booking_id)
    return HTTPException(status.HTTP_403_FORBIDDEN)

@router.get("/")
async def get_bookings(
    session = Depends(get_db),
    cur_user = Depends(get_current_user_from_token)):
    return await get_clients_bookings(session, cur_user.id)

@router.post("/")
async def create_new_booking(booking: BookingCreate, 
                            session = Depends(get_db),
                            cur_user = Depends(get_current_user_from_token)):
    return await create_booking(session, booking, cur_user.id)

@router.delete("/{booking_id}")
async def delete_booking(booking_id: int,
                         session = Depends(get_db),
                         cur_user = Depends(get_current_user_from_token)):
    bookings = await get_client_bookings_by_user_id(session, cur_user.id)
    if booking_id in bookings:
        return await delete_booking_by_id(session, booking_id)
    elif await is_admin(session, cur_user.id):
        return await delete_booking_by_id(session, booking_id)
    return HTTPException(status.HTTP_403_FORBIDDEN)

# @router.patch("/{booking_id}")
# async def dpatch_booking(booking_id: int,
#                          booking_data: BookingUpdate,
#                          session = Depends(get_db),
#                          cur_user = Depends(get_current_user_from_token)):
#     return await update_booking(session, booking_id, booking_data)

@router.put("/{booking_id}")
async def put_patch_booking(booking_id: int,
                         booking_data: BookingCreate,
                         session = Depends(get_db),
                         cur_user = Depends(get_current_user_from_token)):
        bookings = await get_client_bookings_by_user_id(session, cur_user.id)
        if booking_id in bookings:
            return await put_booking(session, cur_user.id, booking_id, booking_data)
        elif await is_admin(session, cur_user.id):
            return await put_booking(session, cur_user.id, booking_id, booking_data)
        return HTTPException(status.HTTP_403_FORBIDDEN)
