from uuid import UUID
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from app.api.dependencies.authentication import get_current_user
from app.api.schemas.auth import (
    AuthenticationResponse,
    LoginImagesRequest,
    LoginImagesResponse,
    LoginRequest,
    RegisterRequest,
    RegisterRepetitionRequest,
    RepetitionAttemptResponse,
    RepetitionHistoryResponse,
    RegistrationProgressResponse,
    UserResponse,
)
from app.infrastructure.database.models.user import User
from app.application.auth.image_selection import (
    InsufficientImageCatalogError,
    RegisteredImageUnavailableError,
)
from app.application.auth.service import (
    AuthService,
    DuplicateAccountError,
    InvalidAuthenticationError,
    InvalidRegistrationError,
    InvalidSelectionError,
    RegistrationProgress,
)
from app.application.auth.tokens import ACCESS_TOKEN_TTL_SECONDS, TokenConfigurationError
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


def make_registration_progress(
    progress: RegistrationProgress,
) -> RegistrationProgressResponse:
    return RegistrationProgressResponse(
        registration_id=str(progress.registration_id),
        completed=progress.user is not None,
        attempt_correct=progress.attempt_correct,
        consecutive_successes=progress.consecutive_successes,
        access_token=progress.token,
        expires_in=ACCESS_TOKEN_TTL_SECONDS if progress.token else None,
        user=(
            UserResponse(
                id=str(progress.user.id),
                username=progress.user.username,
                email=progress.user.email,
            )
            if progress.user is not None
            else None
        ),
    )


@router.post("/register", response_model=RegistrationProgressResponse, status_code=201)
def register(
    request: RegisterRequest,
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> RegistrationProgressResponse:
    try:
        progress = service.start_registration(
            request.username,
            request.email,
            request.image_id,
            request.image_width,
            request.image_height,
            [(point.x, point.y) for point in request.points],
            tolerance_radius=request.tolerance_radius,
        )
    except DuplicateAccountError as error:
        raise HTTPException(409, "Username or email already registered.") from error
    except InvalidSelectionError as error:
        raise HTTPException(422, "Invalid Passpoints selection.") from error
    except TokenConfigurationError as error:
        raise HTTPException(
            503,
            "Authentication is not configured. Set AUTH_TOKEN_SECRET to at least 32 bytes and restart the API.",
        ) from error
    return make_registration_progress(progress)


@router.post(
    "/register/{registration_id}/repetitions",
    response_model=RegistrationProgressResponse,
)
def register_repetition(
    registration_id: UUID,
    request: RegisterRepetitionRequest,
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> RegistrationProgressResponse:
    try:
        progress = service.register_repetition(
            registration_id, [(point.x, point.y) for point in request.points]
        )
    except InvalidRegistrationError as error:
        raise HTTPException(404, "Registration session not found or already completed.") from error
    except DuplicateAccountError as error:
        raise HTTPException(409, "Username or email already registered.") from error
    except TokenConfigurationError as error:
        raise HTTPException(
            503,
            "Authentication is not configured. Set AUTH_TOKEN_SECRET to at least 32 bytes and restart the API.",
        ) from error
    return make_registration_progress(progress)


@router.delete("/register/{registration_id}", status_code=204)
def cancel_registration(
    registration_id: UUID,
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> Response:
    service.cancel_registration(registration_id)
    return Response(status_code=204)


@router.get("/repetition-history", response_model=RepetitionHistoryResponse)
def repetition_history(
    user: Annotated[User, Depends(get_current_user)],
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> RepetitionHistoryResponse:
    attempts = service.get_repetition_history(user.id)
    if attempts is None:
        return RepetitionHistoryResponse(
            has_history=False,
            attempts=[],
            total_attempts=0,
            failures=0,
            attempts_to_goal=None,
        )
    response_attempts = [
        RepetitionAttemptResponse(
            attempt_number=attempt.attempt_number,
            is_correct=attempt.is_correct,
            consecutive_successes=attempt.consecutive_successes,
            created_at=attempt.created_at,
        )
        for attempt in attempts
    ]
    return RepetitionHistoryResponse(
        has_history=bool(response_attempts),
        attempts=response_attempts,
        total_attempts=len(response_attempts),
        failures=sum(not attempt.is_correct for attempt in attempts),
        attempts_to_goal=next(
            (
                attempt.attempt_number
                for attempt in attempts
                if attempt.consecutive_successes >= 3
            ),
            None,
        ),
    )


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