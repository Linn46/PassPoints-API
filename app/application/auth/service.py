from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.application.analysis.service import AnalysisService
from app.application.auth.tokens import (
    ACCESS_TOKEN_TTL_SECONDS,
    TokenConfigurationError,
    create_access_token,
)
from app.application.passpoints.method import Passpoints
from app.core.config.settings import settings
from app.domain.point import Point
from app.geometry.delaunay.validator import DelaunayValidationError
from app.infrastructure.database.models.graphical_password import GraphicalPassword
from app.infrastructure.database.models.user import User
from app.infrastructure.database.repositories.graphical_password_repository import (
    GraphicalPasswordRepository,
)
from app.infrastructure.database.repositories.user_repository import UserRepository


class DuplicateAccountError(ValueError):
    pass


class InvalidSelectionError(ValueError):
    pass


class WeakSelectionError(ValueError):
    pass


class InvalidAuthenticationError(ValueError):
    pass


class AuthService:
    def __init__(self, session: Session, token_secret: str | None = None) -> None:
        self._session = session
        self._users = UserRepository(session)
        self._credentials = GraphicalPasswordRepository(session)
        self._token_secret = settings.auth_token_secret if token_secret is None else token_secret

    def register(
        self,
        username: str,
        email: str,
        image_id: str,
        image_width: int,
        image_height: int,
        points: list[tuple[float, float]],
    ) -> tuple[User, str, int]:
        if self._users.get_by_username(username) or self._users.get_by_email(email):
            raise DuplicateAccountError
        domain_points = [Point(x, y) for x, y in points]
        try:
            analysis = AnalysisService().analyze(domain_points, image_width, image_height)
        except DelaunayValidationError as error:
            raise InvalidSelectionError from error
        if analysis.security.is_weak:
            raise WeakSelectionError
        try:
            verifier = Passpoints.create_credential(
                image_id, image_width, image_height, points
            )
        except ValueError as error:
            raise InvalidSelectionError from error

        user = User(username=username, email=email, password_hash=verifier)
        graphical_password = GraphicalPassword(
            user=user,
            image_id=image_id,
            verifier=verifier,
        )
        try:
            self._session.add_all([user, graphical_password])
            self._session.flush()
            token = create_access_token(user.id, username, self._token_secret)
            self._session.commit()
        except IntegrityError as error:
            self._session.rollback()
            raise DuplicateAccountError from error
        except BaseException:
            self._session.rollback()
            raise
        return user, token, ACCESS_TOKEN_TTL_SECONDS

    def login(
        self,
        email: str,
        image_id: str,
        image_width: int,
        image_height: int,
        points: list[tuple[float, float]],
    ) -> tuple[User, str, int]:
        user = self._users.get_by_email(email)
        if user is None or not user.is_active:
            raise InvalidAuthenticationError
        credentials = self._credentials.list_active_by_user_and_image(user.id, image_id)
        matching_credential = next(
            (
                credential
                for credential in credentials
                if Passpoints.verify_credential(
                image_id, image_width, image_height, points, credential.verifier
            )
            ),
            None,
        )
        if matching_credential is None:
            raise InvalidAuthenticationError
        if user.password_hash is None:
            user.password_hash = matching_credential.verifier
            self._session.commit()
        token = create_access_token(user.id, user.username, self._token_secret)
        return user, token, ACCESS_TOKEN_TTL_SECONDS