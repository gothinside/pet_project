from pydantic import BaseModel, EmailStr, Field, field_validator, validator
from typing import List, Optional, Annotated
from datetime import date, datetime
from fastapi import HTTPException, status
import re


LETTER_MATCH_PATTERN = re.compile(r"^[а-яА-Яa-zA-Z\-]+$")
PASSWORD_PATTERN = re.compile(r"^[A-Za-z\d]+$")


class UserBase(BaseModel):
    email: EmailStr
    is_active: bool = True

class UserCreate(UserBase):
    password_hash: str = Field(min_length=5)

    @field_validator("password_hash")
    def passwrod_validator(cls, value: str):
        if not PASSWORD_PATTERN.match(value):
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                detail="Password should contains only letters and digits")
        return value
    
class UserUpdate(BaseModel):
    email: EmailStr = None
    is_active: bool  = None
    password_hash: Annotated[str, Field(..., min_length=5)] = None

    @field_validator("password_hash")
    def passwrod_validator(cls, value: str):
        if not PASSWORD_PATTERN.match(value) and value:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                detail="Password should contains only letters and digits")
        return value
    
class User_In_Db(UserCreate):
    id: int
    class Config:
        orm_mode = True

class User(UserBase):
    id: int
    clients: List["Client"] = []

    class Config:
        orm_mode = True

class ClientBase(BaseModel):
    first_name: str = Field(min_length=1, max_length=255)
    last_name: str  = Field(min_length=1, max_length=255)
    phone_number: str = Field(min_length=8, max_length=255)

class ClientCreate(ClientBase):
    pass

class ClientUpdate(BaseModel):
    first_name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    last_name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    phone_number: Optional[str] = Field(default=None, min_length=8, max_length=255)


class Client(ClientBase):
    id: int
    bookings: List["Booking"] = []
    users: List[User] = []

    class Config:
        orm_mode = True


class RoomBase(BaseModel):
    room_num: int = Field(ge=1)
    category_id: int
    is_active: bool = True

class RoomCreate(RoomBase):
    pass

class RoomUpdate(BaseModel):
    room_num: Annotated[Optional[int], Field(ge=1)] = None
    category_id: Optional[int] = None
    is_active: Optional[bool] = None
class Room(RoomBase):
    bookings: List["Booking"] = []
    category: "Category"

    class Config:
        orm_mode = True

class PaymentBase(BaseModel):
    amount: int
    payment_date: date

class PaymentCreate(PaymentBase):
    pass

class PaymentUpdate(BaseModel):
    amount: Optional[int] = None
    payment_date: Optional[date] = None

class Payment(PaymentBase):
    id: int
    bookings: List["Booking"] = []

    class Config:
        orm_mode = True

class ServiceBase(BaseModel):
    service_name: str = Field(min_length=1, max_length=255)
    service_price: int = Field(default=0, ge=0)
    is_active: Optional[bool] = True

class ServiceCreate(ServiceBase):
    pass

class ServiceUpdate(BaseModel):
    service_name: Annotated[Optional[str], Field(min_length=1, max_length=255)] = None
    service_price: Annotated[Optional[int], Field(gt=0)] = None
    is_active: Optional[bool] = None
 
class Service(ServiceBase):
    service_id: int
    bookings: List["Booking"] = []

    class Config:
        orm_mode = True

class CategoryBase(BaseModel):
    category_name: str = Field(min_length=1, max_length=255)
    price: int = Field(ge=2000, default=2000)
    beds: int = Field(default=1, ge=1)
    tables: int = Field(default=1, ge=1)
    is_tv: bool = True
    is_wifi: bool = True

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(BaseModel):
    category_name:  Annotated[Optional[str], Field(min_length=1, max_length=255)] = None
    price: Annotated[Optional[int], Field(ge=2000)] = None
    beds: Annotated[Optional[int], Field(ge=1)] = None
    tables: Annotated[Optional[int], Field(ge=1)] = None
    is_tv: Optional[bool] =  None
    is_wifi: Optional[bool] = None

class Category(CategoryBase):
    id: int
    rooms: List["Room"] = []

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str


class BookingBase(BaseModel):
    join_date: datetime
    out_date: datetime
    room_num: int = Field(gt = 0)
    @validator("out_date")
    def out_data_validator(cls, value: datetime, values: dict[str, datetime]):
        if value < values["join_date"]:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                detail="Wrong")
        return value

class BookingCreate(BaseModel):
    booking_data: BookingBase
    services_ids: List[int]
    clients: List[ClientCreate]
    @field_validator("clients")
    def out_data_validator(cls, value: List[ClientCreate]):
        if len([i.phone_number for i in value]) != len(set([i.phone_number for i in value])):
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                detail="Wrong")
        return value
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "booking_data": {
                        "join_date": "2024-07-27T18:41:23.244Z",
                        "out_date": "2024-08-27T18:41:23.244Z",
                        "room_num": 2
                    },
                    "services_ids": [],
                    "clients": [{
                        "first_name": "Name",
                        "last_name": "Lastname",
                        "phone_number": "8-000-000-00-00"
                    }]
                }
            ]
        }
    }

class BookingUpdate(BaseModel):
    join_date: Optional[datetime] = None
    out_date: Optional[datetime] = None
    room_num: Optional[int] = None
    

class Booking(BookingBase):
    id: int
    client: ClientBase
    rooms: List[RoomBase] = []
    payments: List[PaymentBase] = []
    services: List[ServiceBase] = []

    class Config:
        orm_mode = True