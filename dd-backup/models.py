from sqlalchemy import Column, Table, Integer, String, Date, Boolean, ForeignKey, DateTime, TIMESTAMP
from dd.database import Base, engine
from sqlalchemy.orm import relationship
from sqlalchemy import func
from sqlalchemy.dialects.postgresql import UUID
import asyncio


user_role = Table(
    "user_role",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("role_id", Integer, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True)
)

client_user = Table(
    "client_user",
    Base.metadata,
    Column("client_id", Integer, ForeignKey("clients.id", ondelete="CASCADE"), primary_key=True),
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
)

client_booking = Table(
    "client_booking",
    Base.metadata,
    Column("client_id", Integer, ForeignKey("clients.id", ondelete="CASCADE"), primary_key=True),
    Column("booking_id", Integer, ForeignKey("bookings.id", ondelete="CASCADE"), primary_key=True)
)


booking_payment = Table(
    "booking_payment",
    Base.metadata,
    Column("booking_id", Integer, ForeignKey("bookings.id", ondelete="CASCADE"), primary_key=True),
    Column("payment_id", Integer, ForeignKey("payments.id", ondelete="CASCADE"), primary_key=True)
)

booking_service = Table(
    "booking_service",
    Base.metadata,
    Column("booking_id", Integer, ForeignKey("bookings.id", ondelete="CASCADE"), primary_key=True),
    Column("service_id", Integer, ForeignKey("services.service_id", ondelete="CASCADE"), primary_key=True)
)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(1000), nullable=False)
    is_active = Column(Boolean, default=True, index=True)
    clients = relationship("Client", secondary=client_user, back_populates="users")
    roles = relationship("Role", secondary=user_role, back_populates="users")

class Client(Base):
    __tablename__ = "clients"
    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(255), nullable=False)
    last_name = Column(String(255), nullable=False)
    phone_number = Column(String(20), nullable=False, unique=True, index=True)
    bookings = relationship("Booking", secondary=client_booking, back_populates="clients")
    users = relationship("User", secondary=client_user, back_populates="clients")

class Booking(Base):
    __tablename__ = "bookings"
    id = Column(Integer, primary_key=True, autoincrement=True)
    join_date = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    out_date = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    room_num = Column(Integer, ForeignKey("rooms.room_num", ondelete="Cascade"), nullable=False)
    clients = relationship("Client", secondary=client_booking, back_populates="bookings")
    payments = relationship("Payment", secondary=booking_payment, back_populates="bookings")
    services = relationship("Service", secondary=booking_service, back_populates="bookings")

class Room(Base):
    __tablename__ = "rooms"
    room_num = Column(Integer, nullable=False, primary_key=True)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="CASCADE"), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    category = relationship("Category", back_populates="rooms")

class Payment(Base):
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True, autoincrement=True)
    amount = Column(Integer, nullable=False)
    payment_date = Column(DateTime, nullable=False)
    bookings = relationship("Booking", secondary=booking_payment, back_populates="payments")

class Service(Base):
    __tablename__ = "services"
    service_id = Column(Integer, primary_key=True, autoincrement=True)
    service_name = Column(String(255), unique=True, nullable=False, index = True)
    service_price = Column(Integer)
    is_active = Column(Boolean, nullable=False, default=True)
    bookings = relationship("Booking", secondary=booking_service, back_populates="services")

class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, autoincrement=True)
    category_name = Column(String(255), unique=True, nullable=False, index=True)
    price = Column(Integer, nullable=False)
    beds = Column(Integer, default=1, nullable=False)
    tables = Column(Integer, default=1, nullable=False)
    is_tv = Column(Boolean, default=True, nullable=False)
    is_wifi = Column(Boolean, default=True, nullable=False)
    rooms = relationship("Room", back_populates="category")

class Role(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True, autoincrement=True)
    role_name = Column(String, unique=True, nullable=False)
    users = relationship("User", secondary="user_role", back_populates="roles")

