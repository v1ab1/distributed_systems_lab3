from uuid import uuid4
from datetime import datetime
from unittest.mock import AsyncMock

import pytest

from fastapi import status
from fastapi.testclient import TestClient

from app.dependencies import get_privilege_service
from app.presentation.api.main import app
from app.presentation.api.schemas import MeResponse, HistoryItem


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


class TestMeEndpoints:
    def test_get_me_success(self, client, mock_privilege_service):
        username = "testuser"
        ticket_uid = uuid4()
        expected_response = MeResponse(
            balance=1500,
            status="GOLD",
            history=[
                HistoryItem(
                    date=datetime.now(),
                    ticketUid=ticket_uid,
                    balanceDiff=1500,
                    operationType="FILL_IN_BALANCE",
                )
            ],
        )
        mock_privilege_service.get_me.return_value = expected_response

        response = client.get("/v1/me", headers={"X-User-Name": username})

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["balance"] == expected_response.balance
        assert data["status"] == expected_response.status
        assert len(data["history"]) == 1
        assert data["history"][0]["ticketUid"] == str(ticket_uid)
        assert data["history"][0]["balanceDiff"] == 1500
        assert data["history"][0]["operationType"] == "FILL_IN_BALANCE"

    def test_get_me_empty_history(self, client, mock_privilege_service):
        username = "testuser"
        expected_response = MeResponse(balance=0, status="BRONZE", history=[])
        mock_privilege_service.get_me.return_value = expected_response

        response = client.get("/v1/me", headers={"X-User-Name": username})

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["balance"] == 0
        assert data["status"] == "BRONZE"
        assert data["history"] == []

    def test_get_me_missing_header(self, client, mock_privilege_service):
        response = client.get("/v1/me")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
