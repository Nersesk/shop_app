import uuid

import bcrypt
from fastadmin import register, SqlAlchemyModelAdmin
from sqlalchemy import select, update
from fastapi_users.password import PasswordHelper

from ..auth.models import User
from ..session_create import session_maker
from .f_users import fastapi_users
from .schemas import UserCreate

@register(User, sqlalchemy_sessionmaker=session_maker)
class UserAdmin(SqlAlchemyModelAdmin):
    exclude = ("hashed_password",)
    list_display = ("id", "name", "email", "is_superuser", "is_active")
    list_display_links = ("id", "email")
    list_filter = ("id", "email", "is_superuser", "is_active")
    search_fields = ("email",)

    async def authenticate(self, email: str, password: str) -> uuid.UUID | int | None:
        sessionmaker = self.get_sessionmaker()
        async with sessionmaker() as session:
            query = select(self.model_cls).filter_by(email=email, is_superuser=True)
            result = await session.scalars(query)
            obj = result.first()
            if not obj:
                return None
            if not PasswordHelper().verify_and_update(password, obj.hashed_password)[0]:
                return None
            return obj.id

    async def change_password(self, id: uuid.UUID | int, password: str) -> None:
        sessionmaker = self.get_sessionmaker()
        async with sessionmaker() as session:
            hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
            query = update(self.model_cls).where(User.id.in_([id])).values(hashed_password=hashed_password)
            await session.execute(query)
            await session.commit()

    async def orm_save_upload_field(self, obj, field: str, base64: str) -> None:
        sessionmaker = self.get_sessionmaker()
        async with sessionmaker() as session:
            # handle file save logic separately if needed
            query = update(self.model_cls).where(User.id.in_([obj.id])).values(**{field: base64})
            await session.execute(query)
            await session.commit()

    async def save_model(self, id: uuid.UUID | int | None, payload: dict) -> dict | None:
        """This method is used to save orm/db model object.

        :params id: an id of object.
        :params payload: a payload from request.
        :return: A saved object or None.
        """
        user_data = UserCreate(**payload, password="some_fancy_password")
        async for user_manager in fastapi_users.get_user_manager():
            user = await user_manager.create(user_data)
            return user


            # obj = await super().save_model(id, payload)
        #
        # fields = self.get_model_fields_with_widget_types(with_m2m=False, with_upload=False)
        # password_fields = [field.name for field in fields if field.form_widget_type == WidgetType.PasswordInput]
        # if obj and id is None and password_fields:
        #     # save hashed password for create
        #     pk_name = self.get_model_pk_name(self.model_cls)
        #     pk = obj[pk_name]
        #     password_values = [payload[field] for field in password_fields if field in payload]
        #     if password_values:
        #         await self.change_password(pk, password_values[0])
        # return obj