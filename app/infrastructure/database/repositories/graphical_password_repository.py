from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infrastructure.database.models.graphical_password import GraphicalPassword


class GraphicalPasswordRepository:
    def __init__(self, session: Session):
        self.session = session

    def add(self, graphical_password: GraphicalPassword) -> GraphicalPassword:
        self.session.add(graphical_password)
        self.session.flush()
        return graphical_password

    def list_by_user(self, user_id: UUID) -> list[GraphicalPassword]:
        return list(
            self.session.scalars(
                select(GraphicalPassword).where(
                    GraphicalPassword.user_id == user_id
                )
            )
        )

    def list_active_by_user_and_image(
        self, user_id: UUID, image_id: str
    ) -> list[GraphicalPassword]:
        return list(
            self.session.scalars(
                select(GraphicalPassword).where(
                    GraphicalPassword.user_id == user_id,
                    GraphicalPassword.image_id == image_id,
                    GraphicalPassword.is_active.is_(True),
                )
            )
        )
