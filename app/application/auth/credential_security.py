from argon2 import PasswordHasher, Type
from argon2.exceptions import (
    InvalidHashError,
    VerificationError,
    VerifyMismatchError,
)


_password_hasher = PasswordHasher(
    time_cost=2,
    memory_cost=19_456,
    parallelism=1,
    hash_len=32,
    salt_len=16,
    type=Type.ID,
)


def hash_secret(secret: str) -> str:
    return _password_hasher.hash(secret)


def verify_secret(secret: str, encoded_hash: str) -> bool:
    try:
        return _password_hasher.verify(encoded_hash, secret)
    except (InvalidHashError, VerificationError, VerifyMismatchError):
        return False

