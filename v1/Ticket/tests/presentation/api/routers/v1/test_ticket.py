import uuid

from unittest.mock import AsyncMock

import pytest

from fastapi import status
from fastapi.testclient import TestClient

from app.dependencies import get_ticket_service
from app.services.enums import TicketStatus
from app.services.exceptions import (
    TicketNotFoundError,
    InsufficientBalanceError,
)
from app.presentation.api.main import app
from app.presentation.api.schemas import (
    TicketResponse,
    TicketPurchaseResponse,
)


@pytest.fixture
def mock_ticket_service():
    return AsyncMock()


@pytest.fixture
def client(mock_ticket_service):
    async def override_get_ticket_service():
        return mock_ticket_service

    app.dependency_overrides[get_ticket_service] = override_get_ticket_service
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


class TestTicketEndpoints:
    def test_get_all_tickets_success(self, client, mock_ticket_service):
        ticket_uid = uuid.uuid4()
        expected_tickets = [
            TicketResponse(
                id=1,
                ticket_uid=ticket_uid,
                username="testuser",
                flight_number="AFL031",
                price=1500,
                status=TicketStatus.PAID,
            )
        ]
        mock_ticket_service.get_all.return_value = (expected_tickets, 1)

        response = client.get("/v1/tickets", params={"page": 1, "size": 10})

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["page"] == 1
        assert data["pageSize"] == 10
        assert data["totalElements"] == 1
        assert len(data["items"]) == 1

    def test_purchase_ticket_success(self, client, mock_ticket_service):
        from datetime import UTC, datetime

        username = "testuser"
        ticket_uid = uuid.uuid4()
        expected_response = TicketPurchaseResponse(
            ticketUid=ticket_uid,
            flightNumber="AFL031",
            price=1500,
            paidByMoney=1500,
            paidByBonuses=0,
            status=TicketStatus.PAID,
            date=datetime.now(UTC),
        )
        mock_ticket_service.purchase_ticket.return_value = expected_response

        response = client.post(
            "/v1/tickets",
            json={"flightNumber": "AFL031", "price": 1500, "paidFromBalance": False},
            headers={"X-User-Name": username},
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["flightNumber"] == "AFL031"
        assert data["price"] == 1500
        assert "Location" in response.headers

    def test_purchase_ticket_insufficient_balance(self, client, mock_ticket_service):
        username = "testuser"
        mock_ticket_service.purchase_ticket.side_effect = InsufficientBalanceError(balance=500, required=1500)

        response = client.post(
            "/v1/tickets",
            json={"flightNumber": "AFL031", "price": 1500, "paidFromBalance": True},
            headers={"X-User-Name": username},
        )

        assert response.status_code == status.HTTP_402_PAYMENT_REQUIRED

    def test_purchase_ticket_missing_header(self, client, mock_ticket_service):
        response = client.post(
            "/v1/tickets",
            json={"flightNumber": "AFL031", "price": 1500, "paidFromBalance": False},
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_get_ticket_by_uid_success(self, client, mock_ticket_service):
        ticket_uid = uuid.uuid4()
        expected_response = TicketResponse(
            id=1,
            ticket_uid=ticket_uid,
            username="testuser",
            flight_number="AFL031",
            price=1500,
            status=TicketStatus.PAID,
        )
        mock_ticket_service.get_by_ticket_uid.return_value = expected_response

        response = client.get(f"/v1/tickets/{ticket_uid}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["ticket_uid"] == str(ticket_uid)
        assert data["username"] == "testuser"

    def test_get_ticket_by_uid_not_found(self, client, mock_ticket_service):
        ticket_uid = uuid.uuid4()
        mock_ticket_service.get_by_ticket_uid.side_effect = TicketNotFoundError(str(ticket_uid))

        response = client.get(f"/v1/tickets/{ticket_uid}")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_tickets_by_username_success(self, client, mock_ticket_service):
        username = "testuser"
        ticket_uid = uuid.uuid4()
        expected_tickets = [
            TicketResponse(
                id=1,
                ticket_uid=ticket_uid,
                username=username,
                flight_number="AFL031",
                price=1500,
                status=TicketStatus.PAID,
            )
        ]
        mock_ticket_service.get_by_username.return_value = (expected_tickets, 1)

        response = client.get(f"/v1/tickets/user/{username}", params={"page": 1, "size": 10})

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["totalElements"] == 1
        assert len(data["items"]) == 1

    def test_cancel_ticket_success(self, client, mock_ticket_service):
        ticket_uid = uuid.uuid4()
        username = "testuser"
        mock_ticket_service.cancel_ticket.return_value = None

        response = client.delete(
            f"/v1/tickets/{ticket_uid}",
            headers={"X-User-Name": username},
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_cancel_ticket_not_found(self, client, mock_ticket_service):
        ticket_uid = uuid.uuid4()
        username = "testuser"
        mock_ticket_service.cancel_ticket.side_effect = TicketNotFoundError(str(ticket_uid))

        response = client.delete(
            f"/v1/tickets/{ticket_uid}",
            headers={"X-User-Name": username},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_cancel_ticket_missing_header(self, client, mock_ticket_service):
        ticket_uid = uuid.uuid4()

        response = client.delete(f"/v1/tickets/{ticket_uid}")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
