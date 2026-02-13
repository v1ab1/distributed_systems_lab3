from unittest.mock import AsyncMock

import pytest

from fastapi import status
from fastapi.testclient import TestClient

from app.dependencies import get_privilege_service
from app.services.exceptions import UserNotFoundError
from app.presentation.api.main import app


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


class TestBalanceEndpoints:
    def test_set_user_balance_success(self, client, mock_privilege_service):
        username = "testuser"
        new_balance = 500
        mock_privilege_service.set_user_balance.return_value = None

        response = client.post(
            "/v1/balance",
            json={"balance": new_balance},
            headers={"X-User-Name": username},
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_set_user_balance_user_not_found(self, client, mock_privilege_service):
        username = "nonexistent"
        new_balance = 500
        mock_privilege_service.set_user_balance.side_effect = UserNotFoundError(username=username)

        response = client.post(
            "/v1/balance",
            json={"balance": new_balance},
            headers={"X-User-Name": username},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_set_user_balance_missing_header(self, client, mock_privilege_service):
        response = client.post("/v1/balance", json={"balance": 500})

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_set_user_balance_invalid_body(self, client, mock_privilege_service):
        response = client.post(
            "/v1/balance",
            json={"invalid": "data"},
            headers={"X-User-Name": "testuser"},
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_change_user_balance_success(self, client, mock_privilege_service):
        username = "testuser"
        balance_diff = 50
        mock_privilege_service.change_user_balance.return_value = None

        response = client.put(
            "/v1/balance",
            json={"balance": balance_diff},
            headers={"X-User-Name": username},
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_change_user_balance_negative(self, client, mock_privilege_service):
        username = "testuser"
        balance_diff = -30
        mock_privilege_service.change_user_balance.return_value = None

        response = client.put(
            "/v1/balance",
            json={"balance": balance_diff},
            headers={"X-User-Name": username},
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_change_user_balance_user_not_found(self, client, mock_privilege_service):
        username = "nonexistent"
        balance_diff = 50
        mock_privilege_service.change_user_balance.side_effect = UserNotFoundError(username=username)

        response = client.put(
            "/v1/balance",
            json={"balance": balance_diff},
            headers={"X-User-Name": username},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_change_user_balance_missing_header(self, client, mock_privilege_service):
        response = client.put("/v1/balance", json={"balance": 50})

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_change_user_balance_invalid_body(self, client, mock_privilege_service):
        response = client.put(
            "/v1/balance",
            json={"invalid": "data"},
            headers={"X-User-Name": "testuser"},
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_history_record_success(self, client, mock_privilege_service):
        from uuid import uuid4

        username = "testuser"
        ticket_uid = uuid4()
        balance_diff = 150
        operation_type = "FILL_IN_BALANCE"
        mock_privilege_service.create_history_record.return_value = None

        response = client.post(
            "/v1/balance/history",
            json={
                "ticketUid": str(ticket_uid),
                "balanceDiff": balance_diff,
                "operationType": operation_type,
            },
            headers={"X-User-Name": username},
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_create_history_record_missing_header(self, client, mock_privilege_service):
        from uuid import uuid4

        response = client.post(
            "/v1/balance/history",
            json={
                "ticketUid": str(uuid4()),
                "balanceDiff": 150,
                "operationType": "FILL_IN_BALANCE",
            },
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_history_record_invalid_body(self, client, mock_privilege_service):
        response = client.post(
            "/v1/balance/history",
            json={"invalid": "data"},
            headers={"X-User-Name": "testuser"},
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
