from slowapi import Limiter
from slowapi.util import get_remote_address
from app.core.config import settings


def _get_limiter() -> Limiter:
    if settings.REDIS_URL:
        return Limiter(
            key_func=get_remote_address,
            storage_uri=settings.REDIS_URL,
        )
    return Limiter(key_func=get_remote_address)


limiter = _get_limiter()
