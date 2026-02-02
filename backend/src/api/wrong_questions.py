"""Wrong questions API endpoints."""

from typing import Annotated

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from src.api.dependencies import CurrentUserDep, DatabaseDep
from src.services.ai_analysis import AIAnalysisService
from src.services.wrong_question import (
    SubjectService,
    TagService,
    WrongQuestionService,
)


# Schemas
class SubjectResponse(BaseModel):
    """Subject response schema."""

    id: int
    name: str
    description: str | None


class SubjectCreateRequest(BaseModel):
    """Subject create request schema."""

    name: str = Field(..., min_length=1, max_length=50)
    description: str | None = Field(None, max_length=200)


class TagResponse(BaseModel):
    """Tag response schema."""

    id: int
    name: str
    is_preset: bool


class TagCreateRequest(BaseModel):
    """Tag create request schema."""

    name: str = Field(..., min_length=1, max_length=50)


class WrongQuestionTagResponse(BaseModel):
    """Wrong question tag response schema."""

    id: int
    name: str


class WrongQuestionSubjectResponse(BaseModel):
    """Wrong question subject response schema."""

    id: int
    name: str


class WrongQuestionCreateRequest(BaseModel):
    """Wrong question create request schema."""

    title: str = Field(..., min_length=1, max_length=200)
    subject_id: int = Field(..., gt=0)
    tag_ids: list[int] = Field(default_factory=list)
    image_base64: str = Field(..., min_length=1)


class WrongQuestionUpdateRequest(BaseModel):
    """Wrong question update request schema."""

    title: str | None = Field(None, min_length=1, max_length=200)
    subject_id: int | None = Field(None, gt=0)
    tag_ids: list[int] | None = None
    image_base64: str | None = Field(None, min_length=1)


class WrongQuestionResponse(BaseModel):
    """Wrong question response schema."""

    id: int
    title: str
    subject: WrongQuestionSubjectResponse
    tags: list[WrongQuestionTagResponse]
    image_base64: str | None = None
    analysis_status: str = "pending"
    analysis_result: str | None = None
    analysis_error: str | None = None
    analyzed_at: str | None = None
    created_at: str
    updated_at: str


class WrongQuestionAnalysisResponse(BaseModel):
    """Wrong question analysis response schema."""

    id: int
    analysis_status: str  # pending, processing, completed, failed
    analysis_result: str | None = None
    analysis_error: str | None = None
    analyzed_at: str | None = None


class WrongQuestionListItemResponse(BaseModel):
    """Wrong question list item response schema."""

    id: int
    title: str
    subject: WrongQuestionSubjectResponse
    tags: list[WrongQuestionTagResponse]
    created_at: str
    updated_at: str


# Routers
router = APIRouter(prefix="/wrong-questions", tags=["Wrong Questions"])
subjects_router = APIRouter(prefix="/subjects", tags=["Subjects"])
tags_router = APIRouter(prefix="/tags", tags=["Tags"])

# Services
wrong_question_service = WrongQuestionService()
subject_service = SubjectService()
tag_service = TagService()
ai_analysis_service = AIAnalysisService()


# Wrong Question Routes
@router.post("", status_code=status.HTTP_201_CREATED, response_model=WrongQuestionResponse)
async def create_wrong_question(
    request: WrongQuestionCreateRequest,
    current_user: CurrentUserDep,
    db: DatabaseDep,
) -> WrongQuestionResponse:
    """Create a new wrong question.

    Args:
        request: Wrong question create request
        current_user: Current authenticated user
        db: Database session

    Returns:
        WrongQuestionResponse: Created wrong question

    Raises:
        HTTPException: If subject not found or creation failed
    """
    result = await wrong_question_service.create_wrong_question(
        db=db,
        user_id=current_user.id,
        title=request.title,
        subject_id=request.subject_id,
        tag_ids=request.tag_ids,
        image_base64=request.image_base64,
    )

    if not result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create wrong question. Subject may not exist.",
        )

    return WrongQuestionResponse(**result)


@router.get("", response_model=list[WrongQuestionListItemResponse])
async def get_wrong_questions(
    current_user: CurrentUserDep,
    db: DatabaseDep,
) -> list[WrongQuestionListItemResponse]:
    """Get all wrong questions for the current user.

    Args:
        current_user: Current authenticated user
        db: Database session

    Returns:
        List of wrong questions
    """
    result = await wrong_question_service.get_wrong_questions_by_user(
        db=db, user_id=current_user.id
    )
    return [WrongQuestionListItemResponse(**item) for item in result]


@router.get("/{wrong_question_id}", response_model=WrongQuestionResponse)
async def get_wrong_question(
    wrong_question_id: int,
    current_user: CurrentUserDep,
    db: DatabaseDep,
) -> WrongQuestionResponse:
    """Get a specific wrong question by ID.

    Args:
        wrong_question_id: Wrong question ID
        current_user: Current authenticated user
        db: Database session

    Returns:
        WrongQuestionResponse: Wrong question details

    Raises:
        HTTPException: If wrong question not found
    """
    result = await wrong_question_service.get_wrong_question_by_id(
        db=db, wrong_question_id=wrong_question_id, user_id=current_user.id
    )

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wrong question not found",
        )

    return WrongQuestionResponse(**result)


@router.put("/{wrong_question_id}", response_model=WrongQuestionResponse)
async def update_wrong_question(
    wrong_question_id: int,
    request: WrongQuestionUpdateRequest,
    current_user: CurrentUserDep,
    db: DatabaseDep,
) -> WrongQuestionResponse:
    """Update an existing wrong question.

    Args:
        wrong_question_id: Wrong question ID to update
        request: Wrong question update request
        current_user: Current authenticated user
        db: Database session

    Returns:
        WrongQuestionResponse: Updated wrong question

    Raises:
        HTTPException: If wrong question not found or update failed
    """
    result = await wrong_question_service.update_wrong_question(
        db=db,
        wrong_question_id=wrong_question_id,
        user_id=current_user.id,
        title=request.title,
        subject_id=request.subject_id,
        tag_ids=request.tag_ids,
        image_base64=request.image_base64,
    )

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wrong question not found or subject does not exist",
        )

    return WrongQuestionResponse(**result)


@router.post(
    "/{wrong_question_id}/analyze",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=WrongQuestionAnalysisResponse,
)
async def analyze_wrong_question(
    wrong_question_id: int,
    current_user: CurrentUserDep,
    db: DatabaseDep,
) -> WrongQuestionAnalysisResponse:
    """Trigger AI analysis for a wrong question.

    Args:
        wrong_question_id: Wrong question ID to analyze
        current_user: Current authenticated user
        db: Database session

    Returns:
        WrongQuestionAnalysisResponse: Analysis status

    Raises:
        HTTPException: If wrong question not found
    """
    result = await wrong_question_service.analyze_wrong_question(
        db=db,
        wrong_question_id=wrong_question_id,
        user_id=current_user.id,
        ai_analysis_service=ai_analysis_service,
    )

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wrong question not found",
        )

    return WrongQuestionAnalysisResponse(**result)


# Subject Routes
@subjects_router.get("", response_model=list[SubjectResponse])
async def get_subjects(
    db: DatabaseDep,
) -> list[SubjectResponse]:
    """Get all active subjects.

    Args:
        db: Database session

    Returns:
        List of subjects
    """
    result = await subject_service.get_all_subjects(db=db)
    return [SubjectResponse(**item) for item in result]


@subjects_router.post("", status_code=status.HTTP_201_CREATED, response_model=SubjectResponse)
async def create_subject(
    request: SubjectCreateRequest,
    current_user: CurrentUserDep,
    db: DatabaseDep,
) -> SubjectResponse:
    """Create a new subject (admin only in the future).

    Args:
        request: Subject create request
        current_user: Current authenticated user
        db: Database session

    Returns:
        SubjectResponse: Created subject

    Raises:
        HTTPException: If creation failed (e.g., duplicate name)
    """
    result = await subject_service.create_subject(
        db=db, name=request.name, description=request.description
    )

    if not result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Subject with this name already exists",
        )

    return SubjectResponse(**result)


# Tag Routes
@tags_router.get("", response_model=list[TagResponse])
async def get_tags(
    db: DatabaseDep,
) -> list[TagResponse]:
    """Get all tags.

    Args:
        db: Database session

    Returns:
        List of tags
    """
    result = await tag_service.get_all_tags(db=db)
    return [TagResponse(**item) for item in result]


@tags_router.post("", status_code=status.HTTP_201_CREATED, response_model=TagResponse)
async def create_tag(
    request: TagCreateRequest,
    current_user: CurrentUserDep,
    db: DatabaseDep,
) -> TagResponse:
    """Create a new custom tag.

    Args:
        request: Tag create request
        current_user: Current authenticated user
        db: Database session

    Returns:
        TagResponse: Created tag

    Raises:
        HTTPException: If creation failed (e.g., duplicate name)
    """
    result = await tag_service.create_tag(db=db, name=request.name, is_preset=False)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tag with this name already exists",
        )

    return TagResponse(**result)
