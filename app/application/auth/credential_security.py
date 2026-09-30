from argon2 import PasswordHasher, Type
from argon2.exceptions import InvalidHashError, VerificationError

_hasher = PasswordHasher(
    time_cost=2,
    memory_cost=19_456,
    parallelism=1,
    hash_len=32,
    salt_len=16,
    type=Type.ID,
)

def hash_secret(secret: str) -> str:
    return _hasher.hash(secret)

def verify_secret(secret: str, verifier: str) -> bool:
    try:
        return _hasher.verify(verifier, secret)
    except (InvalidHashError, VerificationError):
        return False
