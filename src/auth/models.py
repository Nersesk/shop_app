from fastapi import Depends
from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTableUUID, SQLAlchemyUserDatabase
from sqlalchemy import String
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from ..models import Base
from ..database import get_async_session

class User(SQLAlchemyBaseUserTableUUID, Base):
    name: Mapped[str] = mapped_column(
        String(length=320), nullable=False
    )
    surname: Mapped[str] = mapped_column(
        String(length=320), nullable=False
    )


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)