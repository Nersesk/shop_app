import uuid
from typing import Optional

from fastapi_users import schemas


class UserRead(schemas.BaseUser[uuid.UUID]):
    name: str
    surname: str


class UserCreate(schemas.BaseUserCreate):
    name: str
    surname: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "user@example.com",
                "password": "strongpassword123",
                "name": "John",
                "surname": "Doe",
                # Excludes is_superuser and is_verified
            }
        }
    }


class UserUpdate(schemas.BaseUserUpdate):
    name: Optional[str] = None
    surname: Optional[str] = None