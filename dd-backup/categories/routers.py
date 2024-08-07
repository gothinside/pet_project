from fastapi import APIRouter, Depends, HTTPException, status
from . import crud
from ..database import SessionLocal, engine
from sqlalchemy.ext.asyncio import AsyncSession
from ..models import Base, User
from ..schemas import CategoryCreate, CategoryUpdate
from ..database import get_db
from ..auth import get_current_user_from_token
from ..admin.utils import is_admin

router = APIRouter(
    prefix="/categories",
    tags=["categories"]
)


@router.get("/")
async def read_items(skip: int = 0, limit: int = 100, session: AsyncSession = Depends(get_db)):
    return await crud.get_categories(session, skip, limit)

@router.post("/")
async def new_category(category: CategoryCreate, 
                      session: AsyncSession = Depends(get_db),
                      cur_user: User = Depends(get_current_user_from_token)):
    if await is_admin(session, cur_user.id):
        return await crud.create_category(session, category)
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

@router.patch("/{category_id}")
async def patch_category(category_id: int, 
                         patch_category: CategoryUpdate,
                         session: AsyncSession = Depends(get_db),
                         cur_user: User = Depends(get_current_user_from_token)):
    if await is_admin(session, cur_user.id):
        return await crud.update_category(session, category_id, patch_category)
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

@router.delete("/{category_id}")
async def delete_category(category_id: int, 
                          session: AsyncSession = Depends(get_db),
                          cur_user: User = Depends(get_current_user_from_token)
                          ):
    if await is_admin(session, cur_user.id):
        return await crud.delete_category(session, category_id)
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)