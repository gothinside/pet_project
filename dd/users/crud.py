from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_
from fastapi import HTTPException, status
from ..models import User, user_role, Role
from ..schemas import UserCreate, UserUpdate
from sqlalchemy import select,  update, insert
from ..auth import Hasher
from ..admin.utils import ROLES, role_from_db
from .utils import is_user_unique_by_email



async def get_user_by_id(db: AsyncSession, user_id: int):
    user = (await db.execute(
        select(User).where(User.id == user_id)
    )).scalar_one_or_none()
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
    return user


async def get_user_by_email(db: AsyncSession, email: str):
    user = (await db.execute(
        select(User).where(User.email == email)
    )).scalar_one_or_none()
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
    return user


async def create_user(db: AsyncSession, user: UserCreate):

    if not await is_user_unique_by_email(db, user.email):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "User already exists")
    
    user.password_hash = Hasher.get_password_hash(user.password_hash)

    new_user = (await db.execute(
        insert(User)
        .returning(User)
        .values(**user.model_dump())
    )).scalar_one_or_none()

    #Не исключена вероятность, что с этой ролью что-то случится в базе
    role = await role_from_db(db, ROLES.ROLE_USER)
    if not role:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Role not found")
    
    role_id = role.id
    user_id = new_user.id

    await db.execute(
            user_role.insert().values(user_id=user_id, role_id=role_id)
        )
    try:
        await db.commit()              
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR,
                            "Server error"
        )
    return await get_user_by_id(db, user_id)



async def update_user(db: AsyncSession, 
                      user_id: int, 
                      user: UserUpdate):
    updated_user = {key:value 
                    if key != "password_hash" 
                    else Hasher.get_password_hash(value) 
                    for key,value in user.model_dump().items() 
                    if value is not None}

    if updated_user == {}:
        raise HTTPException(status.HTTP_400_BAD_REQUEST,
                            detail="You should change one field at least")
    

    pre_patch_user =  await get_user_by_id(db, user_id)
    

    if user.email != pre_patch_user.email and not await is_user_unique_by_email(db = db, email = user.email):
            
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "User already exists")
     
    query = (
        update(User)
        .where(and_(User.id == user_id), User.is_active== True)
        .values(
            updated_user
        )
    )
    
    await db.execute(query)
    await db.commit()
    return await get_user_by_id(db, user_id)
    

async def delete_user(db: AsyncSession, user_id: int):
    user = await get_user_by_id(db, user_id)
    try:         
        await db.delete(user)
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR,
                            "Server error"
        )
    return {"message" : "User was deleted"}