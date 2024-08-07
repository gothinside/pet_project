from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_
from fastapi import HTTPException, status
from ..models import User, user_role, Role
from ..schemas import UserCreate, UserUpdate
from sqlalchemy import select,  update, insert
from ..auth import Hasher
from ..admin.utils import ROLES
from .utils import role_from_db
from ..users.crud import  get_user_by_id
from ..users.utils import is_user_unique_by_email
from sqlalchemy import and_

async def create_admin_user(db: AsyncSession, user: UserCreate):
    if not await is_user_unique_by_email(db, user.email):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "User already exists")
    
    user.password_hash = Hasher.get_password_hash(user.password_hash)

    new_user = (await db.execute(
        insert(User)
        .returning(User)
        .values(**user.model_dump())
    )).scalar_one_or_none()

    #Не исключена вероятность, что с этой ролью что-то случится в базе
    role = await role_from_db(db, ROLES.ROLE_ADMIN)
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

async def add_role(db: AsyncSession, user_id: int, role: ROLES):
    await get_user_by_id(db, user_id)

    roles_of_this_user =  (await db.execute(
        select(Role.role_name).join(User.roles).where(User.id == user_id)
    )).scalars().all()

    if (role in roles_of_this_user):
        raise HTTPException(status.HTTP_400_BAD_REQUEST,
                            "This user already grants")

    role_id = (await db.execute(
        select(Role.id)
        .where(Role.role_name == role))
    ).scalars().one_or_none()
    

    await db.execute(
        user_role.insert().values(user_id = user_id, role_id = role_id )
    )
    try:
        await db.commit()              
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR,
                            "Server error"
        )
    return {"message" : "Role changed sucessfuly"}

async def delete_users_role(db: AsyncSession, user_id: int, role: ROLES):
    await get_user_by_id(db, user_id)

    roles_of_this_user =  (await db.execute(
        select(Role.role_name).join(User.roles).where(User.id == user_id)
    )).scalars().all()

    if (role not in roles_of_this_user):
        raise HTTPException(status.HTTP_400_BAD_REQUEST,
                            "This user not grants")
    role_id = (await db.execute(
        select(Role.id)
        .where(Role.role_name == role))
    ).scalar_one_or_none()
    

    await db.execute(
        user_role.delete().where(and_(user_role.c.role_id == role_id, 
                                      user_role.c.user_id== user_id))
    )

    try:
        await db.commit()              
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR,
                            "Server error"
        )
    return {"message" : "Role deleted"}
    