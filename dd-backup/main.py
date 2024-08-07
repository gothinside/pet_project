
from fastapi import FastAPI
import uvicorn
#from .services import routers as serv_routers
from dd.categories import routers as cat_routers
from dd.users import users_router
from dd.login import login_router
from dd.admin import admin_router
from dd.rooms import rooms_routers
from dd.services import routers as service_routers
from dd.clients import client_routers
from dd.bookings import booking_routers
from dd.redis_cache import lifespan
#from .rooms import routers as room_routers
app = FastAPI(lifespan=lifespan)
#cdapp.include_router(serv_routers.router)
app.include_router(cat_routers.router)
app.include_router(users_router.router)
app.include_router(login_router)
app.include_router(admin_router.router)
app.include_router(rooms_routers.router)
app.include_router(service_routers.router)
app.include_router(client_routers.router)
app.include_router(booking_routers.router)
if __name__ == "__main__":
    # run app on the host and port
    uvicorn.run(app, host="localhost", port="8000")

