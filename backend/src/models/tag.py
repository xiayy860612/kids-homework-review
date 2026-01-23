"""Tag model for wrong questions."""

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base


class Tag(Base):
    """Tag model for categorizing wrong questions.

    Attributes:
        id: Unique identifier for the tag
        name: Tag name (unique)
        is_preset: Whether this is a preset tag (created by admin) or custom
        wrong_questions: Related wrong questions
    """

    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    is_preset: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # Relationships
    wrong_questions: Mapped[list["WrongQuestion"]] = relationship(
        "WrongQuestion",
        secondary="wrong_question_tags",
        back_populates="tags",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Tag(id={self.id}, name='{self.name}', is_preset={self.is_preset})>"
