from fastapi_users.authentication import CookieTransport, AuthenticationBackend

from fastapi_users.authentication import JWTStrategy
from ..configs import settings

def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=settings.SECRET_KEY, lifetime_seconds=3600)

cookie_transport = CookieTransport(cookie_name="shop_session",cookie_max_age=3600)


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=cookie_transport,
    get_strategy=get_jwt_strategy,
)
