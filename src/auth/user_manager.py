import uuid
from typing import Optional

from fastapi import Depends, Request
from fastapi_users import BaseUserManager, UUIDIDMixin, models

from ..services.email_service import email_service
from .models import User, get_user_db
from ..configs import settings

class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = settings.SECRET_KEY
    verification_token_secret = settings.SECRET_KEY

    async def on_after_register(self, user: User, request: Optional[Request] = None):

        print(f"User {user.id} has registered.")

    async def on_after_forgot_password(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        subject = "Password reset request"
        body = f"Password reset request for {user.email}.  Reset token: {token} "
        await email_service.send_email_async(to_email=user.email,
                                 email_subject=subject,
                                 email_body=body)

    async def on_after_request_verify(
            self, user: User, token: str, request: Optional[Request] = None
    ):
        subject = "Verification request"
        verify_url = f"{settings.BASE_URL}/auth/verify?token={token}"
        email_body = f"""Click the link below to verify your email:<br><br>
            <a href="{verify_url}">Verify Email</a>
        """
        email_service.send_email(to_email=user.email, subject=subject, email_body=email_body)
        print(f"Verification requested for user {user.id}. Verification token: {token}")


async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)