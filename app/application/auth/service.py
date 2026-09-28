from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.application.analysis.service import AnalysisService
from app.application.auth.credential_security import hash_secret, verify_secret
from app.application.passpoints.method import Passpoints
from app.application.auth.tokens import (
    ACCESS_TOKEN_TTL_SECONDS,
    TokenConfigurationError,
    create_access_token,
)
from app.core.config.settings import settings
from app.domain.point import Point
from app.geometry.delaunay.validator import DelaunayValidationError
from app.infrastructure.database.models.graphical_password import GraphicalPassword
from app.infrastructure.database.models.user import User
from app.infrastructure.database.repositories.graphical_password_repository import (
    GraphicalPasswordRepository,
)
from app.infrastructure.database.repositories.user_repository import UserRepository


class DuplicateUsernameError(ValueError):
    pass


class InvalidCredentialsError(ValueError):
    pass


class WeakGraphicalPasswordError(ValueError):
    pass


class InvalidGraphicalPasswordError(ValueError):
    pass


class AuthService:
    def __init__(self, session: Session, token_secret: str | None = None) -> None:
        self._session = session
        self._users = UserRepository(session)
        self._graphical_passwords = GraphicalPasswordRepository(session)
        self._token_secret = (
            settings.auth_token_secret if token_secret is None else token_secret
        )

    def register(
        self,
        username: str,
        password: str,
        image_id: str,
        image_width: int,
        image_height: int,
        points: list[tuple[float, float]],
    ) -> User:
        if self._users.get_by_username(username) is not None:
            raise DuplicateUsernameError("Username is already registered.")

        domain_points = [Point(x, y) for x, y in points]
        try:
            analysis = AnalysisService().analyze(
                domain_points, image_width, image_height
            )
        except DelaunayValidationError as error:
            raise InvalidGraphicalPasswordError(
                "The graphical password is not a valid Passpoints selection."
            ) from error
        if analysis.security.is_weak:
            raise WeakGraphicalPasswordError(
                "Weak graphical passwords cannot be registered."
            )

        try:
            graphical_verifier = Passpoints.create_credential(
                image_id, image_width, image_height, points
            )
        except ValueError as error:
            raise InvalidGraphicalPasswordError(
                "The graphical password is not a valid Passpoints selection."
            ) from error

        user = User(username=username, password_hash=hash_secret(password))
        graphical_password = GraphicalPassword(
            user=user,
            image_id=image_id,
            verifier=graphical_verifier,
        )
        try:
            self._session.add_all([user, graphical_password])
            self._session.commit()
        except IntegrityError as error:
            self._session.rollback()
            if self._users.get_by_username(username) is not None:
                raise DuplicateUsernameError(
                    "Username is already registered."
                ) from error
            raise
        except BaseException:
            self._session.rollback()
            raise
        return user

    def login(
        self,
        username: str,
        password: str,
        image_id: str,
        image_width: int,
        image_height: int,
        points: list[tuple[float, float]],
    ) -> tuple[User, str, int]:
        user = self._users.get_by_username(username)
        if user is None or not user.is_active:
            raise InvalidCredentialsError("Invalid credentials.")
        if not verify_secret(password, user.password_hash):
            raise InvalidCredentialsError("Invalid credentials.")

        graphical_credentials = self._graphical_passwords.list_active_by_user_and_image(
            user.id, image_id
        )
        if not any(
            Passpoints.verify_credential(
                image_id,
                image_width,
                image_height,
                points,
                credential.verifier,
            )
            for credential in graphical_credentials
        ):
            raise InvalidCredentialsError("Invalid credentials.")

        token = create_access_token(user.id, user.username, self._token_secret)
        return user, token, ACCESS_TOKEN_TTL_SECONDS