"""Tests for WrongQuestionService, SubjectService, and TagService."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.subject import Subject
from src.models.tag import Tag
from src.models.wrong_question import WrongQuestion
from src.models.wrong_question_tag import WrongQuestionTag
from src.services.wrong_question import (
    SubjectService,
    TagService,
    WrongQuestionService,
)


class TestWrongQuestionService:
    """Tests for WrongQuestionService."""

    @pytest.mark.asyncio
    async def test_get_wrong_questions_by_user_empty(self, test_db: AsyncSession):
        """Test getting wrong questions for user with no questions."""
        service = WrongQuestionService()
        result = await service.get_wrong_questions_by_user(test_db, user_id=1)
        assert result == []

    @pytest.mark.asyncio
    async def test_create_wrong_question_success(self, test_db: AsyncSession):
        """Test creating a wrong question successfully."""
        service = WrongQuestionService()

        # First create a subject
        subject = Subject(name="数学", description="数学科目")
        test_db.add(subject)
        await test_db.commit()
        await test_db.refresh(subject)

        # Create tags
        tag1 = Tag(name="计算错误", is_preset=True)
        tag2 = Tag(name="思路错误", is_preset=True)
        test_db.add(tag1)
        test_db.add(tag2)
        await test_db.commit()
        await test_db.refresh(tag1)
        await test_db.refresh(tag2)

        # Create wrong question
        result = await service.create_wrong_question(
            db=test_db,
            user_id=1,
            title="二次函数求最值问题",
            subject_id=subject.id,
            tag_ids=[tag1.id, tag2.id],
            image_base64="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
        )

        assert result is not None
        assert result["title"] == "二次函数求最值问题"
        assert result["subject"]["id"] == subject.id
        assert result["subject"]["name"] == "数学"
        assert len(result["tags"]) == 2
        assert result["image_base64"] == "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="

    @pytest.mark.asyncio
    async def test_create_wrong_question_invalid_subject(self, test_db: AsyncSession):
        """Test creating a wrong question with invalid subject."""
        service = WrongQuestionService()

        result = await service.create_wrong_question(
            db=test_db,
            user_id=1,
            title="二次函数求最值问题",
            subject_id=999,
            tag_ids=[],
            image_base64="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
        )

        assert result is None

    @pytest.mark.asyncio
    async def test_get_wrong_question_by_id_success(self, test_db: AsyncSession):
        """Test getting a wrong question by ID."""
        service = WrongQuestionService()

        # Create subject
        subject = Subject(name="数学", description="数学科目")
        test_db.add(subject)
        await test_db.commit()
        await test_db.refresh(subject)

        # Create tag
        tag = Tag(name="计算错误", is_preset=True)
        test_db.add(tag)
        await test_db.commit()
        await test_db.refresh(tag)

        # Create wrong question
        wrong_question = WrongQuestion(
            user_id=1,
            title="二次函数求最值问题",
            subject_id=subject.id,
            image_base64="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
        )
        test_db.add(wrong_question)
        await test_db.commit()
        await test_db.refresh(wrong_question)

        # Add tag
        wrong_question_tag = WrongQuestionTag(
            wrong_question_id=wrong_question.id, tag_id=tag.id
        )
        test_db.add(wrong_question_tag)
        await test_db.commit()

        # Get wrong question
        result = await service.get_wrong_question_by_id(
            test_db, wrong_question.id, 1
        )

        assert result is not None
        assert result["id"] == wrong_question.id
        assert result["title"] == "二次函数求最值问题"

    @pytest.mark.asyncio
    async def test_get_wrong_question_by_id_not_found(self, test_db: AsyncSession):
        """Test getting a non-existent wrong question."""
        service = WrongQuestionService()
        result = await service.get_wrong_question_by_id(test_db, 999, 1)
        assert result is None

    @pytest.mark.asyncio
    async def test_get_wrong_question_by_id_wrong_user(self, test_db: AsyncSession):
        """Test getting a wrong question with wrong user ID."""
        service = WrongQuestionService()

        # Create subject
        subject = Subject(name="数学", description="数学科目")
        test_db.add(subject)
        await test_db.commit()
        await test_db.refresh(subject)

        # Create wrong question for user 1
        wrong_question = WrongQuestion(
            user_id=1,
            title="二次函数求最值问题",
            subject_id=subject.id,
            image_base64="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
        )
        test_db.add(wrong_question)
        await test_db.commit()
        await test_db.refresh(wrong_question)

        # Try to get with user 2
        result = await service.get_wrong_question_by_id(test_db, wrong_question.id, 2)
        assert result is None

    @pytest.mark.asyncio
    async def test_update_wrong_question_success(self, test_db: AsyncSession):
        """Test updating a wrong question successfully."""
        service = WrongQuestionService()

        # Create subject
        subject = Subject(name="数学", description="数学科目")
        test_db.add(subject)
        await test_db.commit()
        await test_db.refresh(subject)

        # Create wrong question
        wrong_question = WrongQuestion(
            user_id=1,
            title="二次函数求最值问题",
            subject_id=subject.id,
            image_base64="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
        )
        test_db.add(wrong_question)
        await test_db.commit()
        await test_db.refresh(wrong_question)

        # Update
        result = await service.update_wrong_question(
            db=test_db,
            wrong_question_id=wrong_question.id,
            user_id=1,
            title="新的标题",
        )

        assert result is not None
        assert result["title"] == "新的标题"

    @pytest.mark.asyncio
    async def test_update_wrong_question_not_found(self, test_db: AsyncSession):
        """Test updating a non-existent wrong question."""
        service = WrongQuestionService()

        result = await service.update_wrong_question(
            db=test_db,
            wrong_question_id=999,
            user_id=1,
            title="新的标题",
        )

        assert result is None


class TestSubjectService:
    """Tests for SubjectService."""

    @pytest.mark.asyncio
    async def test_get_all_subjects_empty(self, test_db: AsyncSession):
        """Test getting all subjects when none exist."""
        service = SubjectService()
        result = await service.get_all_subjects(test_db)
        assert result == []

    @pytest.mark.asyncio
    async def test_get_all_subjects_with_inactive(self, test_db: AsyncSession):
        """Test getting all active subjects excludes inactive ones."""
        service = SubjectService()

        # Create subjects
        subject1 = Subject(name="数学", description="数学科目", is_active=True)
        subject2 = Subject(name="物理", description="物理科目", is_active=False)
        test_db.add(subject1)
        test_db.add(subject2)
        await test_db.commit()

        result = await service.get_all_subjects(test_db)

        assert len(result) == 1
        assert result[0]["name"] == "数学"

    @pytest.mark.asyncio
    async def test_create_subject_success(self, test_db: AsyncSession):
        """Test creating a subject successfully."""
        service = SubjectService()

        result = await service.create_subject(
            db=test_db, name="化学", description="化学科目"
        )

        assert result is not None
        assert result["name"] == "化学"
        assert result["description"] == "化学科目"

    @pytest.mark.asyncio
    async def test_create_subject_duplicate_name(self, test_db: AsyncSession):
        """Test creating a subject with duplicate name."""
        service = SubjectService()

        # Create first subject
        subject = Subject(name="数学", description="数学科目")
        test_db.add(subject)
        await test_db.commit()

        # Try to create duplicate
        result = await service.create_subject(
            db=test_db, name="数学", description="另一描述"
        )

        assert result is None


class TestTagService:
    """Tests for TagService."""

    @pytest.mark.asyncio
    async def test_get_all_tags_empty(self, test_db: AsyncSession):
        """Test getting all tags when none exist."""
        service = TagService()
        result = await service.get_all_tags(test_db)
        assert result == []

    @pytest.mark.asyncio
    async def test_get_all_tags_with_preset_and_custom(self, test_db: AsyncSession):
        """Test getting all tags includes both preset and custom."""
        service = TagService()

        # Create tags
        tag1 = Tag(name="计算错误", is_preset=True)
        tag2 = Tag(name="自定义标签", is_preset=False)
        test_db.add(tag1)
        test_db.add(tag2)
        await test_db.commit()

        result = await service.get_all_tags(test_db)

        assert len(result) == 2
        assert any(t["name"] == "计算错误" and t["is_preset"] for t in result)
        assert any(t["name"] == "自定义标签" and not t["is_preset"] for t in result)

    @pytest.mark.asyncio
    async def test_create_tag_success(self, test_db: AsyncSession):
        """Test creating a tag successfully."""
        service = TagService()

        result = await service.create_tag(db=test_db, name="自定义标签", is_preset=False)

        assert result is not None
        assert result["name"] == "自定义标签"
        assert result["is_preset"] is False

    @pytest.mark.asyncio
    async def test_create_tag_duplicate_name(self, test_db: AsyncSession):
        """Test creating a tag with duplicate name."""
        service = TagService()

        # Create first tag
        tag = Tag(name="计算错误", is_preset=True)
        test_db.add(tag)
        await test_db.commit()

        # Try to create duplicate
        result = await service.create_tag(db=test_db, name="计算错误", is_preset=False)

        assert result is None
