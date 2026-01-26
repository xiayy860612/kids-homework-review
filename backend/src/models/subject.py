"""Subject model for wrong questions."""

from sqlalchemy import Boolean, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class Subject(Base):
    """Subject model for categorizing wrong questions.

    Attributes:
        id: Unique identifier for the subject
        name: Subject name (unique)
        description: Optional subject description
        is_active: Whether the subject is active
    """

    __tablename__ = "subjects"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String(200), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    def __repr__(self) -> str:
        return f"<Subject(id={self.id}, name='{self.name}')>"
