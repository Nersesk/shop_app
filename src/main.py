import os

import uvicorn
from fastapi import FastAPI
from starlette.staticfiles import StaticFiles
from fastadmin import fastapi_app as admin_app
import fastadmin
from src.auth.f_users import fastapi_users
from src.auth.authentiaction_backend import auth_backend
from src.auth.schemas import UserRead, UserCreate, UserUpdate
from src.products.routers import products_router
from src.configs import MEDIA_DIR
from src.auth.admin import *
app = FastAPI()
app.include_router(products_router)
app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)

app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)

app.mount("/media", StaticFiles(directory=MEDIA_DIR), name="media")
app.mount("/admin", admin_app)

os.environ["ADMIN_USER_MODEL"] = "User"
os.environ["ADMIN_USER_MODEL_USERNAME_FIELD"] = "email"
os.environ["ADMIN_SECRET_KEY"] = "lbyhf1BQX0z4m0oNhQmdrG0JFuL33kQU"

admin_settings = fastadmin.settings.settings

admin_params = {
    "ADMIN_SECRET_KEY": "lbyhf1BQX0z4m0oNhQmdrG0JFuL33kQU",
    "ADMIN_USER_MODEL": "User",
    "ADMIN_USER_MODEL_USERNAME_FIELD": "email"
}

@app.on_event("startup")
async def startup_event():
    for key in dir(admin_settings):
        if key.isupper() and key in admin_params:
            setattr(admin_settings, key, admin_params[key])

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)