from datetime import datetime, timedelta, timezone
from uuid import UUID

import jwt


ACCESS_TOKEN_TTL_SECONDS = 1800


class TokenConfigurationError(RuntimeError):
    pass


def create_access_token(user_id: UUID, username: str, secret: str) -> str:
    if len(secret.encode("utf-8")) < 32:
        raise TokenConfigurationError("AUTH_TOKEN_SECRET must contain at least 32 bytes.")
    now = datetime.now(timezone.utc)
    return jwt.encode(
        {
            "sub": str(user_id),
            "username": username,
            "iat": now,
            "exp": now + timedelta(seconds=ACCESS_TOKEN_TTL_SECONDS),
        },
        secret,
        algorithm="HS256",
    )
