"""Wrong question service for business logic."""

from datetime import UTC, datetime
from typing import Any

from openai import OpenAIError
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.services.ai_analysis import AIAnalysisService
from src.models.subject import Subject
from src.models.tag import Tag
from src.models.wrong_question import WrongQuestion
from src.models.wrong_question_tag import WrongQuestionTag


class WrongQuestionService:
    """Service for wrong question operations."""

    async def get_wrong_questions_by_user(
        self, db: AsyncSession, user_id: int
    ) -> list[dict[str, Any]]:
        """Get all wrong questions for a specific user.

        Args:
            db: Database session
            user_id: User ID to filter by

        Returns:
            List of wrong question dictionaries with related data
        """
        stmt = (
            select(WrongQuestion)
            .where(WrongQuestion.user_id == user_id)
            .options(
                selectinload(WrongQuestion.subject),
                selectinload(WrongQuestion.tags),
            )
            .order_by(WrongQuestion.created_at.desc())
        )
        result = await db.execute(stmt)
        wrong_questions = result.scalars().all()

        return [
            {
                "id": wq.id,
                "title": wq.title,
                "subject": {
                    "id": wq.subject.id,
                    "name": wq.subject.name,
                },
                "tags": [{"id": tag.id, "name": tag.name} for tag in wq.tags],
                "created_at": wq.created_at.isoformat(),
                "updated_at": wq.updated_at.isoformat(),
            }
            for wq in wrong_questions
        ]

    async def get_wrong_question_by_id(
        self, db: AsyncSession, wrong_question_id: int, user_id: int
    ) -> dict[str, Any] | None:
        """Get a specific wrong question by ID.

        Args:
            db: Database session
            wrong_question_id: Wrong question ID
            user_id: User ID for ownership check

        Returns:
            Wrong question dictionary or None if not found
        """
        stmt = (
            select(WrongQuestion)
            .where(WrongQuestion.id == wrong_question_id)
            .where(WrongQuestion.user_id == user_id)
            .options(
                selectinload(WrongQuestion.subject),
                selectinload(WrongQuestion.tags),
            )
        )
        result = await db.execute(stmt)
        wrong_question = result.unique().scalar_one_or_none()

        if not wrong_question:
            return None

        return {
            "id": wrong_question.id,
            "title": wrong_question.title,
            "subject": {
                "id": wrong_question.subject.id,
                "name": wrong_question.subject.name,
            },
            "tags": [
                {"id": tag.id, "name": tag.name} for tag in wrong_question.tags
            ],
            "image_base64": wrong_question.image_base64,
            "analysis_status": wrong_question.analysis_status,
            "analysis_result": wrong_question.analysis_result,
            "analysis_error": wrong_question.analysis_error,
            "analyzed_at": (
                wrong_question.analyzed_at.isoformat()
                if wrong_question.analyzed_at
                else None
            ),
            "created_at": wrong_question.created_at.isoformat(),
            "updated_at": wrong_question.updated_at.isoformat(),
        }

    async def create_wrong_question(
        self,
        db: AsyncSession,
        user_id: int,
        title: str,
        subject_id: int,
        tag_ids: list[int],
        image_base64: str,
    ) -> dict[str, Any] | None:
        """Create a new wrong question.

        Args:
            db: Database session
            user_id: User ID creating the wrong question
            title: Title of the wrong question
            subject_id: Subject ID
            tag_ids: List of tag IDs
            image_base64: Base64 encoded image

        Returns:
            Created wrong question dictionary or None if creation failed
        """
        try:
            # Verify subject exists
            subject_stmt = select(Subject).where(Subject.id == subject_id)
            subject_result = await db.execute(subject_stmt)
            subject = subject_result.scalar_one_or_none()
            if not subject:
                return None

            # Create wrong question
            wrong_question = WrongQuestion(
                user_id=user_id,
                title=title,
                subject_id=subject_id,
                image_base64=image_base64,
            )
            db.add(wrong_question)
            await db.flush()

            # Add tags
            if tag_ids:
                # Verify tags exist
                tags_stmt = select(Tag).where(Tag.id.in_(tag_ids))
                tags_result = await db.execute(tags_stmt)
                tags = tags_result.scalars().all()

                for tag in tags:
                    wrong_question_tag = WrongQuestionTag(
                        wrong_question_id=wrong_question.id, tag_id=tag.id
                    )
                    db.add(wrong_question_tag)

            await db.commit()

            # Return the created wrong question with relations
            return await self.get_wrong_question_by_id(db, wrong_question.id, user_id)

        except IntegrityError:
            await db.rollback()
            return None

    async def update_wrong_question(
        self,
        db: AsyncSession,
        wrong_question_id: int,
        user_id: int,
        title: str | None = None,
        subject_id: int | None = None,
        tag_ids: list[int] | None = None,
        image_base64: str | None = None,
    ) -> dict[str, Any] | None:
        """Update an existing wrong question.

        Args:
            db: Database session
            wrong_question_id: Wrong question ID to update
            user_id: User ID for ownership check
            title: New title (optional)
            subject_id: New subject ID (optional)
            tag_ids: New list of tag IDs (optional)
            image_base64: New base64 encoded image (optional)

        Returns:
            Updated wrong question dictionary or None if not found
        """
        stmt = (
            select(WrongQuestion)
            .where(
                WrongQuestion.id == wrong_question_id,
                WrongQuestion.user_id == user_id,
            )
            .options(selectinload(WrongQuestion.subject))
        )
        result = await db.execute(stmt)
        wrong_question = result.unique().scalar_one_or_none()

        if not wrong_question:
            return None

        try:
            # Update fields if provided
            if title is not None:
                wrong_question.title = title
            if subject_id is not None:
                # Verify subject exists
                subject_stmt = select(Subject).where(Subject.id == subject_id)
                subject_result = await db.execute(subject_stmt)
                subject = subject_result.scalar_one_or_none()
                if not subject:
                    return None
                wrong_question.subject_id = subject_id
            if image_base64 is not None:
                wrong_question.image_base64 = image_base64

            # Update tags if provided
            if tag_ids is not None:
                # Delete existing tags
                delete_stmt = select(WrongQuestionTag).where(
                    WrongQuestionTag.wrong_question_id == wrong_question_id
                )
                delete_result = await db.execute(delete_stmt)
                existing_tags = delete_result.scalars().all()
                for tag in existing_tags:
                    await db.delete(tag)

                # Add new tags
                if tag_ids:
                    # Verify tags exist
                    tags_stmt = select(Tag).where(Tag.id.in_(tag_ids))
                    tags_result = await db.execute(tags_stmt)
                    tags = tags_result.scalars().all()

                    for tag in tags:
                        wrong_question_tag = WrongQuestionTag(
                            wrong_question_id=wrong_question.id, tag_id=tag.id
                        )
                        db.add(wrong_question_tag)

            await db.commit()

            # Return the updated wrong question with relations
            return await self.get_wrong_question_by_id(db, wrong_question.id, user_id)

        except IntegrityError:
            await db.rollback()
            return None

    async def analyze_wrong_question(
        self, db: AsyncSession, wrong_question_id: int, user_id: int,
        ai_analysis_service: AIAnalysisService
    ) -> dict[str, object] | None:
        """Analyze a wrong question image using AI.

        Args:
            db: Database session
            wrong_question_id: Wrong question ID to analyze
            user_id: User ID for ownership check

        Returns:
            Updated wrong question dictionary or None if failed
        """
        # 1. Get wrong question and verify ownership
        stmt = select(WrongQuestion).where(
            WrongQuestion.id == wrong_question_id,
            WrongQuestion.user_id == user_id,
        )
        result = await db.execute(stmt)
        wrong_question = result.unique().scalar_one_or_none()

        if not wrong_question:
            return None

        # 2. Update status to processing
        wrong_question.analysis_status = "processing"
        await db.commit()

        try:
            # 3. Call AI model for analysis
            analysis_result = await ai_analysis_service.call_ai_model(
                image_base64=wrong_question.image_base64,
                title=wrong_question.title,
            )

            # 4. Save analysis result
            wrong_question.analysis_status = "completed"
            wrong_question.analysis_result = analysis_result
            wrong_question.analysis_error = None
            wrong_question.analyzed_at = datetime.now(UTC)

            await db.commit()
            await db.refresh(wrong_question)

            # 5. Return updated data
            return self._serialize_wrong_question(wrong_question)

        except OpenAIError as e:
            # API call failed
            wrong_question.analysis_status = "failed"
            wrong_question.analysis_error = f"AI API 调用失败: {str(e)}"
            await db.commit()
            return None

        except Exception as e:
            # Other errors
            wrong_question.analysis_status = "failed"
            wrong_question.analysis_error = f"解析失败: {str(e)}"
            await db.commit()
            return None

    def _serialize_wrong_question(
        self, wrong_question: WrongQuestion
    ) -> dict[str, object]:
        """Serialize wrong question to dictionary.

        Args:
            wrong_question: WrongQuestion model instance

        Returns:
            Dictionary representation
        """
        return {
            "id": wrong_question.id,
            "title": wrong_question.title,
            "subject": {
                "id": wrong_question.subject.id,
                "name": wrong_question.subject.name,
            },
            "tags": [
                {"id": tag.id, "name": tag.name} for tag in wrong_question.tags
            ],
            "image_base64": wrong_question.image_base64,
            "analysis_status": wrong_question.analysis_status,
            "analysis_result": wrong_question.analysis_result,
            "analysis_error": wrong_question.analysis_error,
            "analyzed_at": (
                wrong_question.analyzed_at.isoformat()
                if wrong_question.analyzed_at
                else None
            ),
            "created_at": wrong_question.created_at.isoformat(),
            "updated_at": wrong_question.updated_at.isoformat(),
        }



class SubjectService:
    """Service for subject operations."""

    async def get_all_subjects(self, db: AsyncSession) -> list[dict[str, Any]]:
        """Get all active subjects.

        Args:
            db: Database session

        Returns:
            List of subject dictionaries
        """
        stmt = select(Subject).where(Subject.is_active == True).order_by(Subject.id)
        result = await db.execute(stmt)
        subjects = result.scalars().all()

        return [
            {"id": subject.id, "name": subject.name, "description": subject.description}
            for subject in subjects
        ]

    async def create_subject(
        self, db: AsyncSession, name: str, description: str | None = None
    ) -> dict[str, Any] | None:
        """Create a new subject.

        Args:
            db: Database session
            name: Subject name
            description: Optional description

        Returns:
            Created subject dictionary or None if creation failed
        """
        try:
            subject = Subject(name=name, description=description)
            db.add(subject)
            await db.commit()
            await db.refresh(subject)

            return {
                "id": subject.id,
                "name": subject.name,
                "description": subject.description,
            }
        except IntegrityError:
            await db.rollback()
            return None


class TagService:
    """Service for tag operations."""

    async def get_all_tags(self, db: AsyncSession) -> list[dict[str, Any]]:
        """Get all tags.

        Args:
            db: Database session

        Returns:
            List of tag dictionaries
        """
        stmt = select(Tag).order_by(Tag.id)
        result = await db.execute(stmt)
        tags = result.scalars().all()

        return [
            {"id": tag.id, "name": tag.name, "is_preset": tag.is_preset} for tag in tags
        ]

    async def create_tag(
        self, db: AsyncSession, name: str, is_preset: bool = False
    ) -> dict[str, Any] | None:
        """Create a new tag.

        Args:
            db: Database session
            name: Tag name
            is_preset: Whether this is a preset tag

        Returns:
            Created tag dictionary or None if creation failed
        """
        try:
            tag = Tag(name=name, is_preset=is_preset)
            db.add(tag)
            await db.commit()
            await db.refresh(tag)

            return {"id": tag.id, "name": tag.name, "is_preset": tag.is_preset}
        except IntegrityError:
            await db.rollback()
            return None
