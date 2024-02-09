from datetime import datetime
from uuid import uuid4, UUID
from sqlalchemy import CheckConstraint, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base


class Publication(Base):
    __tablename__ = "publication"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    text: Mapped[str] = mapped_column(String(length=4096), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow,
    )
    author_id: Mapped[UUID] = mapped_column(
        ForeignKey("auth_user.id", ondelete="CASCADE"),
        nullable=False,
    )
    counter_of_votes: Mapped[int] = mapped_column(server_default="0")
    publication_rating: Mapped[int] = mapped_column(default=0)

    __table_args__ = (
        CheckConstraint("counter_of_votes >= 0", name="positive_value_non_negative"),
    )


class Rating(Base):
    __tablename__ = "rating"

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("auth_user.id", ondelete=("CASCADE")),
    )
    publication_id: Mapped[UUID] = mapped_column(
        ForeignKey("publication.id", ondelete=("CASCADE")),
        primary_key=True,
    )
    like_is_toggeled: Mapped[bool | None] = mapped_column(default=None)
