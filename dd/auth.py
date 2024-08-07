from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from typing import Optional
import jwt
from jwt.exceptions import InvalidTokenError
from fastapi.security import OAuth2PasswordBearer
from fastapi import HTTPException, Depends, status
from .database import SessionLocal
from .database import get_db
from .models import User, user_role, Role
from sqlalchemy import select
from .security import *
from .users.crud import get_user_by_email

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login/token")

    


async def authenticate_user(
    email: str, password: str, db: AsyncSession
):
    user = await get_user_by_email(db, email)
    if not Hasher.verify_password(password, user.password_hash):
        return
    return user


async def get_current_user_from_token(
    token: str = Depends(oauth2_scheme), 
    db: AsyncSession = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )
    try:
        payload = jwt.decode(
            token, SECRET_KEY, algorithms=[ALGORITHM]
        )
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception
    
    user = await get_user_by_email(db, email)
    if user is None:
        raise credentials_exception
    
    return user
