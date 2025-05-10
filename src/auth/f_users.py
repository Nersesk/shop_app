from fastapi_users import FastAPIUsers
from .models import User
import uuid
from .authentiaction_backend import  auth_backend
from .user_manager import get_user_manager


fastapi_users = FastAPIUsers[User, uuid.UUID](
    get_user_manager,
    [auth_backend],
)