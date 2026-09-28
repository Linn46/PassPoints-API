from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.schemas.auth import (
    AuthenticationResponse,
    LoginRequest,
    RegisteredUserResponse,
    RegisterRequest,
)
from app.application.auth.service import (
    AuthService,
    DuplicateUsernameError,
    InvalidGraphicalPasswordError,
    InvalidCredentialsError,
    WeakGraphicalPasswordError,
)
from app.application.auth.tokens import TokenConfigurationError
from app.infrastructure.database.session import get_db_session


router = APIRouter(prefix="/auth", tags=["Authentication"])


def get_auth_service(
    session: Annotated[Session, Depends(get_db_session)],
) -> AuthService:
    return AuthService(session)


def _points(request: RegisterRequest | LoginRequest) -> list[tuple[float, float]]:
    return [(point.x, point.y) for point in request.points]


@router.post(
    "/register",
    response_model=RegisteredUserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    request: RegisterRequest,
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> RegisteredUserResponse:
    try:
        user = service.register(
            request.username,
            request.password,
            request.image_id,
            request.image_width,
            request.image_height,
            _points(request),
        )
    except DuplicateUsernameError as error:
        raise HTTPException(status_code=409, detail="Username already registered.") from error
    except WeakGraphicalPasswordError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    except InvalidGraphicalPasswordError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    return RegisteredUserResponse(id=str(user.id), username=user.username)


@router.post("/login", response_model=AuthenticationResponse)
def login(
    request: LoginRequest,
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> AuthenticationResponse:
    try:
        user, token, expires_in = service.login(
            request.username,
            request.password,
            request.image_id,
            request.image_width,
            request.image_height,
            _points(request),
        )
    except InvalidCredentialsError as error:
        raise HTTPException(status_code=401, detail="Invalid credentials.") from error
    except TokenConfigurationError as error:
        raise HTTPException(
            status_code=503, detail="Authentication is not configured."
        ) from error
    return AuthenticationResponse(
        access_token=token,
        expires_in=expires_in,
        user=RegisteredUserResponse(id=str(user.id), username=user.username),
    )