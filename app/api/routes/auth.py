from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.schemas.auth import (
    AuthenticationResponse,
    LoginImagesRequest,
    LoginImagesResponse,
    LoginRequest,
    RegisterRequest,
    UserResponse,
)
from app.application.auth.image_selection import (
    InsufficientImageCatalogError,
    RegisteredImageUnavailableError,
)
from app.application.auth.service import (
    AuthService,
    DuplicateAccountError,
    InconsistentPasswordError,
    InvalidAuthenticationError,
    InvalidSelectionError,
)
from app.application.auth.tokens import TokenConfigurationError
from app.infrastructure.database.session import get_db_session


router = APIRouter(prefix="/auth", tags=["Authentication"])


def get_auth_service(
    session: Annotated[Session, Depends(get_db_session)],
) -> AuthService:
    return AuthService(session)


def make_response(user, token: str, expires_in: int) -> AuthenticationResponse:
    return AuthenticationResponse(
        access_token=token,
        expires_in=expires_in,
        user=UserResponse(id=str(user.id), username=user.username, email=user.email),
    )


@router.post("/register", response_model=AuthenticationResponse, status_code=201)
def register(
    request: RegisterRequest,
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> AuthenticationResponse:
    try:
        confirmation_points = (
            [[(point.x, point.y) for point in seq] for seq in request.confirmation_points]
            if request.confirmation_points is not None
            else None
        )
        user, token, expires_in = service.register(
            request.username,
            request.email,
            request.image_id,
            request.image_width,
            request.image_height,
            [(point.x, point.y) for point in request.points],
            confirmation_points=confirmation_points,
            repetition_count=request.repetition_count,
        )
    except DuplicateAccountError as error:
        raise HTTPException(409, "Username or email already registered.") from error
    except InconsistentPasswordError as error:
        raise HTTPException(
            422,
            "The graphical password must be repeated consistently two more times.",
        ) from error
    except InvalidSelectionError as error:
        raise HTTPException(422, "Invalid Passpoints selection.") from error
    except TokenConfigurationError as error:
        raise HTTPException(
            503,
            "Authentication is not configured. Set AUTH_TOKEN_SECRET to at least 32 bytes and restart the API.",
        ) from error
    return make_response(user, token, expires_in)


@router.post("/login-images", response_model=LoginImagesResponse)
def login_images(
    request: LoginImagesRequest,
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> LoginImagesResponse:
    try:
        image_ids = service.login_image_options(request.email, request.image_ids)
    except InsufficientImageCatalogError as error:
        raise HTTPException(
            422, "At least three different images are required."
        ) from error
    except RegisteredImageUnavailableError as error:
        raise HTTPException(
            409, "The registered image is unavailable in the current catalog."
        ) from error
    return LoginImagesResponse(image_ids=image_ids)


@router.post("/login", response_model=AuthenticationResponse)
def login(
    request: LoginRequest,
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> AuthenticationResponse:
    try:
        identifier = request.email or request.username or ""
        user, token, expires_in = service.login(
            identifier,
            request.image_id,
            request.image_width,
            request.image_height,
            [(point.x, point.y) for point in request.points],
        )
    except InvalidAuthenticationError as error:
        raise HTTPException(401, "Invalid credentials.") from error
    except TokenConfigurationError as error:
        raise HTTPException(
            503,
            "Authentication is not configured. Set AUTH_TOKEN_SECRET to at least 32 bytes and restart the API.",
        ) from error
    return make_response(user, token, expires_in)