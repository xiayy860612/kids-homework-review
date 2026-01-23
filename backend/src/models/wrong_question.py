"""WrongQuestion model for storing student wrong questions."""

from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base


class WrongQuestion(Base):
    """WrongQuestion model for storing student wrong questions.

    Attributes:
        id: Unique identifier for the wrong question
        user_id: ID of the user who created this wrong question
        title: Title of the wrong question
        subject_id: ID of the subject this question belongs to
        image_base64: Base64 encoded image of the wrong question
        created_at: Creation timestamp
        updated_at: Last update timestamp
        subject: Related subject
        tags: Related tags
    """

    __tablename__ = "wrong_questions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    subject_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("subjects.id"), nullable=False
    )
    image_base64: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    # Relationships
    subject: Mapped["Subject"] = relationship(
        "Subject", lazy="joined", innerjoin=True
    )
    tags: Mapped[list["Tag"]] = relationship(
        "Tag",
        secondary="wrong_question_tags",
        back_populates="wrong_questions",
        lazy="joined",
    )

    def __repr__(self) -> str:
        return f"<WrongQuestion(id={self.id}, title='{self.title}', user_id={self.user_id})>"
