from dataclasses import dataclass
from uuid import UUID, uuid4

from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.application.analysis.service import AnalysisService as PatternAnalysisService
from app.application.auth.image_selection import select_login_images
from app.application.auth.tokens import (
    ACCESS_TOKEN_TTL_SECONDS,
    TokenConfigurationError,
    create_access_token,
)
from app.application.passpoints.method import DEFAULT_TOLERANCE_RADIUS, Passpoints
from app.core.config.settings import settings
from app.domain.point import Point
from app.infrastructure.database.models.graphical_password import GraphicalPassword
from app.infrastructure.database.models.registration import (
    RegistrationAttempt,
    RegistrationDraft,
)
from app.infrastructure.database.models.user import User
from app.infrastructure.database.repositories.graphical_password_repository import (
    GraphicalPasswordRepository,
)
from app.infrastructure.database.repositories.user_repository import UserRepository


class DuplicateAccountError(ValueError):
    pass


class InvalidSelectionError(ValueError):
    pass


class InvalidAuthenticationError(ValueError):
    pass


class InvalidRegistrationError(ValueError):
    pass


@dataclass(frozen=True)
class RegistrationProgress:
    registration_id: UUID
    consecutive_successes: int
    attempt_correct: bool
    user: User | None = None
    token: str | None = None


class AuthService:
    def __init__(self, session: Session, token_secret: str | None = None) -> None:
        self._session = session
        self._users = UserRepository(session)
        self._credentials = GraphicalPasswordRepository(session)
        self._token_secret = settings.auth_token_secret if token_secret is None else token_secret

    def start_registration(
        self,
        username: str,
        email: str,
        image_id: str,
        image_width: int,
        image_height: int,
        points: list[tuple[float, float]],
    ) -> RegistrationProgress:
        pending_draft = self._session.scalar(
            select(RegistrationDraft.id).where(
                RegistrationDraft.is_completed.is_(False),
                or_(
                    RegistrationDraft.username == username,
                    RegistrationDraft.email == email,
                ),
            )
        )
        if (
            self._users.get_by_username(username)
            or self._users.get_by_email(email)
            or pending_draft is not None
        ):
            raise DuplicateAccountError
        if len(self._token_secret.encode("utf-8")) < 32:
            raise TokenConfigurationError(
                "AUTH_TOKEN_SECRET must contain at least 32 bytes."
            )
        try:
            verifier = Passpoints.create_credential(
                image_id,
                image_width,
                image_height,
                points,
                DEFAULT_TOLERANCE_RADIUS,
            )
            encrypted_points = Passpoints.encrypt_points(
                image_id,
                image_width,
                image_height,
                points,
                self._token_secret,
                DEFAULT_TOLERANCE_RADIUS,
            )
        except InvalidSelectionError:
            raise
        except ValueError as error:
            raise InvalidSelectionError from error

        self._validate_password_strength(image_width, image_height, points)
        draft = RegistrationDraft(
            username=username,
            email=email,
            image_id=image_id,
            image_width=image_width,
            image_height=image_height,
            verifier=verifier,
            tolerance_radius=DEFAULT_TOLERANCE_RADIUS,
            encrypted_points=encrypted_points,
            consecutive_successes=1,
            attempt_count=1,
        )
        try:
            self._session.add(draft)
            self._session.flush()
            self._session.add(
                RegistrationAttempt(
                    registration_id=draft.id,
                    attempt_number=1,
                    is_correct=True,
                    consecutive_successes=1,
                )
            )
            self._session.commit()
        except IntegrityError as error:
            self._session.rollback()
            raise DuplicateAccountError from error
        except BaseException:
            self._session.rollback()
            raise
        return RegistrationProgress(draft.id, 1, True)

    def register_immediately(
        self,
        username: str,
        email: str,
        image_id: str,
        image_width: int,
        image_height: int,
        points: list[tuple[float, float]],
        confirmation_points: list[list[tuple[float, float]]],
    ) -> RegistrationProgress:
        pending_draft = self._session.scalar(
            select(RegistrationDraft.id).where(
                RegistrationDraft.is_completed.is_(False),
                or_(
                    RegistrationDraft.username == username,
                    RegistrationDraft.email == email,
                ),
            )
        )
        if (
            self._users.get_by_username(username)
            or self._users.get_by_email(email)
            or pending_draft is not None
        ):
            raise DuplicateAccountError
        if len(self._token_secret.encode("utf-8")) < 32:
            raise TokenConfigurationError(
                "AUTH_TOKEN_SECRET must contain at least 32 bytes."
            )
        try:
            starting_verifier = Passpoints.create_credential(
                image_id,
                image_width,
                image_height,
                points,
                DEFAULT_TOLERANCE_RADIUS,
            )
            starting_encrypted_points = Passpoints.encrypt_points(
                image_id,
                image_width,
                image_height,
                points,
                self._token_secret,
                DEFAULT_TOLERANCE_RADIUS,
            )
            max_deviation = 0.0
            tolerance_radius = DEFAULT_TOLERANCE_RADIUS
            for confirmation in confirmation_points:
                measured = Passpoints.measure_repetition_deviations(
                    image_id,
                    image_width,
                    image_height,
                    confirmation,
                    starting_verifier,
                    starting_encrypted_points,
                    DEFAULT_TOLERANCE_RADIUS,
                    self._token_secret,
                )
                if measured is None:
                    raise InvalidSelectionError(
                        "The graphical password must be repeated consistently two more times."
                    )
                reference_points, deviations = measured
                max_safe_radius = Passpoints.max_safe_tolerance_radius(
                    reference_points
                )
                if any(deviation > max_safe_radius for deviation in deviations):
                    raise InvalidSelectionError(
                        "The graphical password must be repeated consistently two more times."
                    )
                max_deviation = max(max_deviation, max(deviations))
            tolerance_radius = Passpoints.estimate_tolerance_radius(
                max_deviation, points
            )
            verifier = Passpoints.create_credential(
                image_id, image_width, image_height, points, tolerance_radius
            )
            encrypted_points = Passpoints.encrypt_points(
                image_id,
                image_width,
                image_height,
                points,
                self._token_secret,
                tolerance_radius,
            )
        except InvalidSelectionError:
            raise
        except ValueError as error:
            raise InvalidSelectionError from error

        self._validate_password_strength(image_width, image_height, points)
        user = User(
            username=username,
            email=email,
            password_hash=verifier,
            graphical_password_repetition_count=2,
            graphical_password_verified=True,
        )
        self._session.add(
            GraphicalPassword(
                user=user,
                image_id=image_id,
                verifier=verifier,
                encrypted_points=encrypted_points,
                tolerance_radius=tolerance_radius,
            )
        )
        try:
            self._session.flush()
            token = create_access_token(user.id, user.username, self._token_secret)
            self._session.commit()
        except IntegrityError as error:
            self._session.rollback()
            raise DuplicateAccountError from error
        except BaseException:
            self._session.rollback()
            raise
        return RegistrationProgress(user.id, 3, True, user, token)

    @staticmethod
    def _validate_password_strength(
        image_width: int,
        image_height: int,
        points: list[tuple[float, float]],
    ) -> None:
        analysis = PatternAnalysisService()
        domain_points = [Point(x=x, y=y) for x, y in points]
        result = analysis.analyze(
            points=domain_points,
            image_width=image_width,
            image_height=image_height,
            method="delaunay_statistical",
        )
        if result.security.is_weak:
            raise InvalidSelectionError(
                "Weak graphical-password patterns are not allowed."
            )

    def register_repetition(
        self, registration_id: UUID, points: list[tuple[float, float]]
    ) -> RegistrationProgress:
        draft = self._session.get(RegistrationDraft, registration_id)
        if draft is None or draft.is_completed or draft.verifier is None:
            raise InvalidRegistrationError

        measured = Passpoints.measure_repetition_deviations(
            draft.image_id,
            draft.image_width,
            draft.image_height,
            points,
            draft.verifier,
            draft.encrypted_points,
            draft.tolerance_radius,
            self._token_secret,
        )
        reference_points, deviations = measured if measured is not None else ([], [])
        max_safe_radius = (
            Passpoints.max_safe_tolerance_radius(reference_points)
            if reference_points
            else 0
        )
        is_correct = bool(deviations) and all(
            deviation <= max_safe_radius for deviation in deviations
        )
        draft.consecutive_successes = (
            draft.consecutive_successes + 1 if is_correct else 0
        )
        if is_correct:
            draft.max_successful_deviation = max(
                draft.max_successful_deviation,
                max(deviations),
            )
        else:
            draft.max_successful_deviation = 0
        draft.attempt_count += 1
        self._session.add(
            RegistrationAttempt(
                registration_id=draft.id,
                attempt_number=draft.attempt_count,
                is_correct=is_correct,
                consecutive_successes=draft.consecutive_successes,
            )
        )

        user = None
        token = None
        if draft.consecutive_successes == 3:
            if (
                self._users.get_by_username(draft.username)
                or self._users.get_by_email(draft.email)
            ):
                self._session.rollback()
                raise DuplicateAccountError
            tolerance_radius = Passpoints.estimate_tolerance_radius(
                draft.max_successful_deviation,
                reference_points,
            )
            verifier = Passpoints.create_credential(
                draft.image_id,
                draft.image_width,
                draft.image_height,
                reference_points,
                tolerance_radius,
            )
            encrypted_points = Passpoints.encrypt_points(
                draft.image_id,
                draft.image_width,
                draft.image_height,
                reference_points,
                self._token_secret,
                tolerance_radius,
            )
            user = User(
                username=draft.username,
                email=draft.email,
                password_hash=verifier,
                graphical_password_repetition_count=draft.consecutive_successes - 1,
                graphical_password_verified=True,
            )
            self._session.add(
                GraphicalPassword(
                    user=user,
                    image_id=draft.image_id,
                    verifier=verifier,
                    encrypted_points=encrypted_points,
                    tolerance_radius=tolerance_radius,
                )
            )
            draft.is_completed = True
            draft.verifier = None
            try:
                self._session.flush()
                draft.user_id = user.id
                token = create_access_token(user.id, user.username, self._token_secret)
                self._session.commit()
            except IntegrityError as error:
                self._session.rollback()
                raise DuplicateAccountError from error
            except BaseException:
                self._session.rollback()
                raise
        else:
            self._session.commit()

        return RegistrationProgress(
            draft.id,
            draft.consecutive_successes,
            is_correct,
            user,
            token,
        )

    def cancel_registration(self, registration_id: UUID) -> None:
        draft = self._session.get(RegistrationDraft, registration_id)
        if draft is not None and not draft.is_completed:
            self._session.delete(draft)
            self._session.commit()

    def get_repetition_history(
        self, user_id: UUID
    ) -> list[RegistrationAttempt] | None:
        registration_id = self._session.scalar(
            select(RegistrationDraft.id)
            .where(
                RegistrationDraft.user_id == user_id,
                RegistrationDraft.is_completed.is_(True),
            )
            .order_by(RegistrationDraft.created_at.desc())
            .limit(1)
        )
        if registration_id is None:
            return None
        return list(
            self._session.scalars(
                select(RegistrationAttempt)
                .where(RegistrationAttempt.registration_id == registration_id)
                .order_by(RegistrationAttempt.attempt_number)
            )
        )

    def login_image_options(
        self, email: str, catalog_image_ids: list[str]
    ) -> list[str]:
        user = self._users.get_by_email(email)
        registered_image_id = None
        if user is not None and user.is_active:
            credentials = self._credentials.list_by_user(user.id)
            active_credential = next(
                (credential for credential in credentials if credential.is_active),
                None,
            )
            if active_credential is not None:
                registered_image_id = active_credential.image_id
        return select_login_images(catalog_image_ids, registered_image_id)

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
        if len(self._token_secret.encode("utf-8")) < 32:
            raise TokenConfigurationError(
                "AUTH_TOKEN_SECRET must contain at least 32 bytes."
            )
        matching_credential = next(
            (
                credential
                for credential in credentials
                if Passpoints.verify_credential(
                    image_id,
                    image_width,
                    image_height,
                    points,
                    credential.verifier,
                    credential.encrypted_points,
                    credential.tolerance_radius,
                    self._token_secret,
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