import pytest

from dd.main import app
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from dd.database import get_db, Base
from fastapi.testclient import TestClient
from httpx import AsyncClient
import asyncio
import asyncpg
from sqlalchemy import text
from dd.auth import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from datetime import timedelta
from dd.schemas import BookingCreate, UserCreate, CategoryCreate, ServiceCreate
from dd.services.crud import create_service
from dd.users.crud import create_user, get_user_by_id, get_user_by_email
from dd.admin.crud import create_admin_user
from dd.security import create_access_token
from dd.categories.crud import create_category
from dd.bookings.crud import create_booking

@pytest.fixture(scope='session')
def event_loop(request):
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


async def override_get_async_session():
    engine = create_async_engine(
    "postgresql+asyncpg://postgres:123@localhost/test_hotel_db",
    future = True
)

    TestSessionLocal = sessionmaker(bind=engine, expire_on_commit=True, class_= AsyncSession)
    Base.metadata.bind = engine
    async with TestSessionLocal() as session:
        yield session

async def get_session():
    engine = create_async_engine(
    "postgresql+asyncpg://postgres:123@localhost/test_hotel_db",
    future = True
)

    TestSessionLocal = sessionmaker(bind=engine, expire_on_commit=True, class_= AsyncSession)
    Base.metadata.bind = engine
    return TestSessionLocal()  

@pytest.fixture(autouse=True, scope='session')
async def prepare_database():
    engine = create_async_engine(
    "postgresql+asyncpg://postgres:123@localhost/test_hotel_db",
    future = True
    )
    Base.metadata.bind = engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

# @pytest.fixture(scope="function", autouse=True)
# async def clean_tables():
#     """Clean data in all tables before running test function"""
#     async with TestSessionLocal() as session:
#         async with session.begin():
#             for table_for_cleaning in ["user_role", "users", "roles",  "rooms", "categories", "services"]:
#                 await session.execute(text(f"""Delete from {table_for_cleaning} cascade;"""))
# # SETUP

@pytest.fixture(scope="session")
async def client() :
    app.dependency_overrides[get_db] = override_get_async_session
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        yield client

@pytest.fixture(scope="function")
async def asyncpg_pool():
    pool = await asyncpg.create_pool(
        "".join("postgresql+asyncpg://postgres:123@localhost/test_hotel_db".split("+asyncpg"))
    )
    yield pool
    pool.close()


@pytest.fixture(scope="session")
async def create_user_role(asyncpg_pool):
        async with asyncpg_pool.acquire() as connection:
            return await connection.fetch(
                """INSERT INTO roles values (1, 'ROLE_USER')
                on conflict do nothing;"""
            )
@pytest.fixture(scope="session", autouse=True)
async def create_new_role(prepare_database):
    engine = create_async_engine(
    "postgresql+asyncpg://postgres:123@localhost/test_hotel_db",
    echo=True,
    future = True
)

    TestSessionLocal = sessionmaker(bind=engine, expire_on_commit=True, class_= AsyncSession)
    Base.metadata.bind = engine
    async with TestSessionLocal() as session:
                async with session.begin():
                    await session.execute(
                        text("""INSERT INTO roles values (1, 'ROLE_USER')
                             on conflict do nothing;""")
                    )
                    await session.commit()

@pytest.fixture(scope="session", autouse=True)
async def create_new_role_admin(prepare_database):
    engine = create_async_engine(
    "postgresql+asyncpg://postgres:123@localhost/test_hotel_db",
    echo=True,
    future = True
)

    TestSessionLocal = sessionmaker(bind=engine, expire_on_commit=True, class_= AsyncSession)
    Base.metadata.bind = engine
    async with TestSessionLocal() as session:
                async with session.begin():
                    await session.execute(
                        text("""INSERT INTO roles values (2, 'ROLE_ADMIN')
                             ON CONFLICT DO NOTHING;""")
                    )
                    await session.commit()

@pytest.fixture()
async def create_new_category():
    engine = create_async_engine(
    "postgresql+asyncpg://postgres:123@localhost/test_hotel_db",
    echo=True,
    future = True
)
    category = {
         "category_name": "econom",
         "price": 2000,
         "beds": 1
    }
    TestSessionLocal = sessionmaker(bind=engine, expire_on_commit=True, class_= AsyncSession)
    Base.metadata.bind = engine
    async with TestSessionLocal() as session:
                    try:
                        await create_category(session,
                                            CategoryCreate(**category))
                    except Exception as e:
                          pass


async def create_new_user():
    session = await get_session()
    new_user = {"email": "1@m.ru",
                "password_hash" : "12345",
                "is_active" : True}
    new_user = UserCreate(
                         **new_user
                    )
    try:
                        user = await create_user(session, new_user)
                        return user
    except Exception as e:
                         return await get_user_by_email(session, user.email)

     

async def create_new_admin(admin: dict):
    engine = create_async_engine(
    "postgresql+asyncpg://postgres:123@localhost/test_hotel_db",
    echo=True,
    future = True
)

    TestSessionLocal = sessionmaker(bind=engine, expire_on_commit=True, class_= AsyncSession)
    Base.metadata.bind = engine
    async with TestSessionLocal() as session:
          new_admin = UserCreate(
               **admin
          )
          admin = await create_admin_user(session, new_admin)
          return admin
    
      

async def get_some_admin():
    some_admin = {
            "email": "adm@mail.ru",
            "password_hash": "123456",
            "is_active": True
      }
    new_admin = UserCreate(
            **some_admin
      )
    engine = create_async_engine(
    "postgresql+asyncpg://postgres:123@localhost/test_hotel_db",
    echo=True,
    future = True
)

    TestSessionLocal = sessionmaker(bind=engine, expire_on_commit=True, class_= AsyncSession)
    Base.metadata.bind = engine
    async with TestSessionLocal() as session:
      try:
        admin = await create_admin_user(session, new_admin)
        return admin
      except Exception as e:
           return new_admin



def create_test_auth_headers_for_user(email: str) -> dict[str, str]:
#     engine = create_async_engine(
#     "postgresql+asyncpg://postgres:123@localhost/test_hotel_db",
#     echo=True,
#     future = True
# )

#     TestSessionLocal = sessionmaker(bind=engine, expire_on_commit=True, class_= AsyncSession)
#     Base.metadata.bind = engine
#     async with TestSessionLocal() as session:
#         await get_user_by_email(session, email)
    access_token = create_access_token(
        data={"sub": email, "other_custom_data": [1, 2, 3, 4]},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return {"Authorization": f"Bearer {access_token}"}

@pytest.fixture
async def create_new_room_id_2(create_new_category):
#     engine = create_async_engine(
#     "postgresql+asyncpg://postgres:123@localhost/test_hotel_db",
#     echo=True,
#     future = True
# )

#     TestSessionLocal = sessionmaker(bind=engine, expire_on_commit=True, class_= AsyncSession)
#     Base.metadata.bind = engine
    session = await get_session()
    if 1:
                async with session.begin():
                    await session.execute(
                        text("""INSERT INTO rooms values (2, 1, True)
                             ON CONFLICT DO NOTHING""")
                    )
                    await session.commit()

@pytest.fixture
async def create_new_serivce():
    service = {
        "service_name": "hotel_room",
    }
#     session = await get_session()
#     engine = create_async_engine(
#     "postgresql+asyncpg://postgres:123@localhost/test_hotel_db",
#     echo=True,
#     future = True
# )

#     TestSessionLocal = sessionmaker(bind=engine, expire_on_commit=True, class_= AsyncSession)
#     Base.metadata.bind = engine
    session = await get_session()
    async with session.begin():
        try:
            await create_service(session, ServiceCreate(**service))
        except Exception as e:
             pass
        
@pytest.fixture
async def create_new_serivce_2():

    service = {
        "service_name": "help_with_1",
    }
    session = await get_session()
    async with session.begin():
        try:
            await create_service(session, ServiceCreate(**service))
        except Exception as e:
             pass
        
@pytest.fixture
async def create_new_room_id_5(create_new_category):
    session = await get_session()
    if 1:
                async with session.begin():
                    await session.execute(
                        text("""INSERT INTO rooms values (7, 1, True)
                             ON CONFLICT DO NOTHING""")
                    )
                    await session.commit()


@pytest.fixture()
async def create_new_category_2():
    category = {
         "category_name": "econom+",
         "price": 2000,
         "beds": 2
    }
    session = await get_session()
    if 1:
         try:
                        await create_category(session,
                                            CategoryCreate(**category))
         except Exception as e:
                          pass
                    
async def create_some_booking():
    #   pass
    booking = {
    "booking_data": {
        "join_date": "2024-07-27T18:41:23.244000Z",
        "out_date": "2024-08-27T18:41:23.244000Z",
        "room_num": 2
    },
    "services_ids": [],
    "clients": [
        {
        "first_name": "Name",
        "last_name": "Lastname",
        "phone_number": "8-000-000-00-00"
        }
    ]
    }
    new_booking = BookingCreate(**booking)
    admin = await get_some_admin()
    session = await get_session()
    
    return  await create_booking(session, new_booking, 1)
