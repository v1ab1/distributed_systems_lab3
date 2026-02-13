from unittest.mock import AsyncMock

import pytest

from fastapi import status
from fastapi.testclient import TestClient

from app.dependencies import get_privilege_service
from app.services.exceptions import UserNotFoundError, UsernameAlreadyExistError
from app.presentation.api.main import app
from app.presentation.api.schemas import PrivilegeResponse


@pytest.fixture
def mock_privilege_service():
    return AsyncMock()


@pytest.fixture
def client(mock_privilege_service):
    async def override_get_privilege_service():
        return mock_privilege_service

    app.dependency_overrides[get_privilege_service] = override_get_privilege_service
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


class TestUsersEndpoints:
    def test_get_user_success(self, client, mock_privilege_service):
        username = "testuser"
        expected_response = PrivilegeResponse(
            id=1,
            username=username,
            status="BRONZE",
            balance=100,
        )
        mock_privilege_service.get_user.return_value = expected_response

        response = client.get("/v1/users", headers={"X-User-Name": username})

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == expected_response.id
        assert data["username"] == expected_response.username
        assert data["status"] == expected_response.status
        assert data["balance"] == expected_response.balance

    def test_get_user_not_found(self, client, mock_privilege_service):
        username = "nonexistent"
        mock_privilege_service.get_user.side_effect = UserNotFoundError(username=username)

        response = client.get("/v1/users", headers={"X-User-Name": username})

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_user_missing_header(self, client, mock_privilege_service):
        response = client.get("/v1/users")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_user_success(self, client, mock_privilege_service):
        username = "newuser"
        mock_privilege_service.create_new_user.return_value = None

        response = client.post("/v1/users", headers={"X-User-Name": username})

        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_create_user_already_exists(self, client, mock_privilege_service):
        username = "testuser"
        mock_privilege_service.create_new_user.side_effect = UsernameAlreadyExistError(username=username)

        response = client.post("/v1/users", headers={"X-User-Name": username})

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_user_missing_header(self, client, mock_privilege_service):
        response = client.post("/v1/users")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_delete_user_success(self, client, mock_privilege_service):
        username = "testuser"
        mock_privilege_service.delete_user.return_value = None

        response = client.delete("/v1/users", headers={"X-User-Name": username})

        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_delete_user_not_found(self, client, mock_privilege_service):
        username = "nonexistent"
        mock_privilege_service.delete_user.side_effect = UserNotFoundError(username=username)

        response = client.delete("/v1/users", headers={"X-User-Name": username})

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_user_missing_header(self, client, mock_privilege_service):
        response = client.delete("/v1/users")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
