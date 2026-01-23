"""WrongQuestionTag association table model."""

from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class WrongQuestionTag(Base):
    """Association table for WrongQuestion and Tag many-to-many relationship.

    Attributes:
        wrong_question_id: ID of the wrong question
        tag_id: ID of the tag
    """

    __tablename__ = "wrong_question_tags"

    wrong_question_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("wrong_questions.id", ondelete="CASCADE"),
        primary_key=True,
    )
    tag_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("tags.id", ondelete="CASCADE"),
        primary_key=True,
    )

    def __repr__(self) -> str:
        return f"<WrongQuestionTag(wrong_question_id={self.wrong_question_id}, tag_id={self.tag_id})>"
