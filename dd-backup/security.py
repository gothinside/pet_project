from datetime import datetime, timedelta
from .settings import ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY, ALGORITHM
from typing import Optional
from passlib.context import CryptContext
import jwt


pwd_context = CryptContext(schemes=["bcrypt"], deprecated = "auto")

class Hasher:
    @staticmethod
    def get_password_hash(password: str) -> bool:
        return pwd_context.hash(password)
    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        return pwd_context.verify(password, hashed_password)
    
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, SECRET_KEY, algorithm=ALGORITHM
    )
    return encoded_jwt