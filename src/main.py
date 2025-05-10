import uvicorn
from fastapi import FastAPI
from starlette.staticfiles import StaticFiles

from src.auth.f_users import fastapi_users
from src.auth.authentiaction_backend import auth_backend
from src.auth.schemas import UserRead, UserCreate, UserUpdate
from src.products.routers import products_router
from src.configs import MEDIA_DIR
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

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)