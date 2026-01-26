"""Tests for wrong questions API endpoints."""

import pytest
from httpx import AsyncClient


class TestWrongQuestionsEndpoints:
    """Tests for /api/wrong-questions endpoints."""

    @pytest.mark.asyncio
    async def test_create_wrong_question_success(self, async_client: AsyncClient):
        """Test creating a wrong question successfully."""
        # Login to get token
        login_response = await async_client.post(
            "/api/auth/login", json={"username": "admin", "password": "password123"}
        )
        token = login_response.json()["access_token"]

        # Create subject first
        subject_response = await async_client.post(
            "/api/subjects",
            json={"name": "数学", "description": "数学科目"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert subject_response.status_code == 201
        subject_id = subject_response.json()["id"]

        # Create tags
        tag_response = await async_client.post(
            "/api/tags",
            json={"name": "计算错误"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert tag_response.status_code == 201
        tag_id = tag_response.json()["id"]

        # Create wrong question
        response = await async_client.post(
            "/api/wrong-questions",
            json={
                "title": "二次函数求最值问题",
                "subject_id": subject_id,
                "tag_ids": [tag_id],
                "image_base64": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
            },
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "二次函数求最值问题"
        assert data["subject"]["id"] == subject_id
        assert len(data["tags"]) == 1

    @pytest.mark.asyncio
    async def test_create_wrong_question_unauthorized(self, async_client: AsyncClient):
        """Test creating a wrong question without authentication."""
        response = await async_client.post(
            "/api/wrong-questions",
            json={
                "title": "二次函数求最值问题",
                "subject_id": 1,
                "tag_ids": [],
                "image_base64": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
            },
        )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_wrong_questions_empty(self, async_client: AsyncClient):
        """Test getting wrong questions when none exist."""
        # Login
        login_response = await async_client.post(
            "/api/auth/login", json={"username": "admin", "password": "password123"}
        )
        token = login_response.json()["access_token"]

        response = await async_client.get(
            "/api/wrong-questions",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        assert response.json() == []

    @pytest.mark.asyncio
    async def test_get_wrong_questions_with_data(self, async_client: AsyncClient):
        """Test getting wrong questions with existing data."""
        # Login
        login_response = await async_client.post(
            "/api/auth/login", json={"username": "admin", "password": "password123"}
        )
        token = login_response.json()["access_token"]

        # Create subject
        subject_response = await async_client.post(
            "/api/subjects",
            json={"name": "数学", "description": "数学科目"},
            headers={"Authorization": f"Bearer {token}"},
        )
        subject_id = subject_response.json()["id"]

        # Create wrong question
        await async_client.post(
            "/api/wrong-questions",
            json={
                "title": "二次函数求最值问题",
                "subject_id": subject_id,
                "tag_ids": [],
                "image_base64": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
            },
            headers={"Authorization": f"Bearer {token}"},
        )

        # Get wrong questions
        response = await async_client.get(
            "/api/wrong-questions",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == "二次函数求最值问题"

    @pytest.mark.asyncio
    async def test_get_wrong_question_by_id_success(self, async_client: AsyncClient):
        """Test getting a specific wrong question by ID."""
        # Login
        login_response = await async_client.post(
            "/api/auth/login", json={"username": "admin", "password": "password123"}
        )
        token = login_response.json()["access_token"]

        # Create subject
        subject_response = await async_client.post(
            "/api/subjects",
            json={"name": "数学", "description": "数学科目"},
            headers={"Authorization": f"Bearer {token}"},
        )
        subject_id = subject_response.json()["id"]

        # Create wrong question
        create_response = await async_client.post(
            "/api/wrong-questions",
            json={
                "title": "二次函数求最值问题",
                "subject_id": subject_id,
                "tag_ids": [],
                "image_base64": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        wrong_question_id = create_response.json()["id"]

        # Get wrong question by ID
        response = await async_client.get(
            f"/api/wrong-questions/{wrong_question_id}",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == wrong_question_id
        assert data["title"] == "二次函数求最值问题"

    @pytest.mark.asyncio
    async def test_get_wrong_question_by_id_not_found(self, async_client: AsyncClient):
        """Test getting a non-existent wrong question."""
        # Login
        login_response = await async_client.post(
            "/api/auth/login", json={"username": "admin", "password": "password123"}
        )
        token = login_response.json()["access_token"]

        response = await async_client.get(
            "/api/wrong-questions/999",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_update_wrong_question_success(self, async_client: AsyncClient):
        """Test updating a wrong question successfully."""
        # Login
        login_response = await async_client.post(
            "/api/auth/login", json={"username": "admin", "password": "password123"}
        )
        token = login_response.json()["access_token"]

        # Create subject
        subject_response = await async_client.post(
            "/api/subjects",
            json={"name": "数学", "description": "数学科目"},
            headers={"Authorization": f"Bearer {token}"},
        )
        subject_id = subject_response.json()["id"]

        # Create wrong question
        create_response = await async_client.post(
            "/api/wrong-questions",
            json={
                "title": "二次函数求最值问题",
                "subject_id": subject_id,
                "tag_ids": [],
                "image_base64": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        wrong_question_id = create_response.json()["id"]

        # Update wrong question
        response = await async_client.put(
            f"/api/wrong-questions/{wrong_question_id}",
            json={"title": "新的标题"},
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "新的标题"

    @pytest.mark.asyncio
    async def test_update_wrong_question_not_found(self, async_client: AsyncClient):
        """Test updating a non-existent wrong question."""
        # Login
        login_response = await async_client.post(
            "/api/auth/login", json={"username": "admin", "password": "password123"}
        )
        token = login_response.json()["access_token"]

        response = await async_client.put(
            "/api/wrong-questions/999",
            json={"title": "新的标题"},
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 404


class TestSubjectsEndpoints:
    """Tests for /api/subjects endpoints."""

    @pytest.mark.asyncio
    async def test_get_subjects_empty(self, async_client: AsyncClient):
        """Test getting subjects when none exist."""
        # Login
        login_response = await async_client.post(
            "/api/auth/login", json={"username": "admin", "password": "password123"}
        )
        token = login_response.json()["access_token"]

        response = await async_client.get(
            "/api/subjects",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        assert response.json() == []

    @pytest.mark.asyncio
    async def test_get_subjects_with_data(self, async_client: AsyncClient):
        """Test getting subjects with existing data."""
        # Login
        login_response = await async_client.post(
            "/api/auth/login", json={"username": "admin", "password": "password123"}
        )
        token = login_response.json()["access_token"]

        # Create subject
        await async_client.post(
            "/api/subjects",
            json={"name": "数学", "description": "数学科目"},
            headers={"Authorization": f"Bearer {token}"},
        )

        # Get subjects
        response = await async_client.get(
            "/api/subjects",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "数学"

    @pytest.mark.asyncio
    async def test_create_subject_success(self, async_client: AsyncClient):
        """Test creating a subject successfully."""
        # Login
        login_response = await async_client.post(
            "/api/auth/login", json={"username": "admin", "password": "password123"}
        )
        token = login_response.json()["access_token"]

        response = await async_client.post(
            "/api/subjects",
            json={"name": "数学", "description": "数学科目"},
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "数学"
        assert data["description"] == "数学科目"

    @pytest.mark.asyncio
    async def test_create_subject_duplicate_name(self, async_client: AsyncClient):
        """Test creating a subject with duplicate name."""
        # Login
        login_response = await async_client.post(
            "/api/auth/login", json={"username": "admin", "password": "password123"}
        )
        token = login_response.json()["access_token"]

        # Create first subject
        await async_client.post(
            "/api/subjects",
            json={"name": "数学", "description": "数学科目"},
            headers={"Authorization": f"Bearer {token}"},
        )

        # Try to create duplicate
        response = await async_client.post(
            "/api/subjects",
            json={"name": "数学", "description": "另一描述"},
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 400


class TestTagsEndpoints:
    """Tests for /api/tags endpoints."""

    @pytest.mark.asyncio
    async def test_get_tags_empty(self, async_client: AsyncClient):
        """Test getting tags when none exist."""
        # Login
        login_response = await async_client.post(
            "/api/auth/login", json={"username": "admin", "password": "password123"}
        )
        token = login_response.json()["access_token"]

        response = await async_client.get(
            "/api/tags",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        assert response.json() == []

    @pytest.mark.asyncio
    async def test_get_tags_with_data(self, async_client: AsyncClient):
        """Test getting tags with existing data."""
        # Login
        login_response = await async_client.post(
            "/api/auth/login", json={"username": "admin", "password": "password123"}
        )
        token = login_response.json()["access_token"]

        # Create tag
        await async_client.post(
            "/api/tags",
            json={"name": "计算错误"},
            headers={"Authorization": f"Bearer {token}"},
        )

        # Get tags
        response = await async_client.get(
            "/api/tags",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "计算错误"

    @pytest.mark.asyncio
    async def test_create_tag_success(self, async_client: AsyncClient):
        """Test creating a tag successfully."""
        # Login
        login_response = await async_client.post(
            "/api/auth/login", json={"username": "admin", "password": "password123"}
        )
        token = login_response.json()["access_token"]

        response = await async_client.post(
            "/api/tags",
            json={"name": "自定义标签"},
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "自定义标签"
        assert data["is_preset"] is False

    @pytest.mark.asyncio
    async def test_create_tag_duplicate_name(self, async_client: AsyncClient):
        """Test creating a tag with duplicate name."""
        # Login
        login_response = await async_client.post(
            "/api/auth/login", json={"username": "admin", "password": "password123"}
        )
        token = login_response.json()["access_token"]

        # Create first tag
        await async_client.post(
            "/api/tags",
            json={"name": "计算错误"},
            headers={"Authorization": f"Bearer {token}"},
        )

        # Try to create duplicate
        response = await async_client.post(
            "/api/tags",
            json={"name": "计算错误"},
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 400
