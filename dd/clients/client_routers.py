from sqlalchemy.ext.asyncio import AsyncSession
from ..models import User, Role
from sqlalchemy import select
from fastapi import APIRouter, Depends, HTTPException, status
from ..schemas import ClientCreate, Client, ClientBase, ClientUpdate
from ..auth import get_current_user_from_token
from ..database import get_db
from .crud import *

router = APIRouter(
    prefix="/clients",
    tags=["clients"]
)

# @router.post("/")
# async def create_new_client(client: Client, 
#                             cur_user = Depends(get_current_user_from_token)):
#     return 1

@router.patch("/{client_id}", response_model = ClientBase)
async def patch_client(client_id: int,
                       client: ClientUpdate,
                       session = Depends(get_db),
                       cur_user = Depends(get_current_user_from_token)):
    return await update_client(session, client, client_id)
