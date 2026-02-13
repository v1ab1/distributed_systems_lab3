import uuid
import asyncio

import pytest

from app.services.enums import TicketStatus
from app.services.exceptions import (
    FlightNotFoundError,
    TicketNotFoundError,
    InsufficientBalanceError,
)
from app.presentation.api.schemas import (
    TicketResponse,
    TicketCreateRequest,
    TicketPurchaseResponse,
)


class TestTicketService:
    def test_get_by_ticket_uid_success(self, ticket_service, mock_ticket_repository, sample_ticket):
        ticket_uid = str(sample_ticket.ticket_uid)
        mock_ticket_repository.get_by_ticket_uid.return_value = sample_ticket

        result = asyncio.run(ticket_service.get_by_ticket_uid(ticket_uid))

        mock_ticket_repository.get_by_ticket_uid.assert_awaited_once_with(ticket_uid)
        assert isinstance(result, TicketResponse)
        assert result.id == sample_ticket.id
        assert result.ticket_uid == sample_ticket.ticket_uid

    def test_get_by_ticket_uid_not_found(self, ticket_service, mock_ticket_repository):
        ticket_uid = str(uuid.uuid4())
        mock_ticket_repository.get_by_ticket_uid.return_value = None

        with pytest.raises(TicketNotFoundError) as exc_info:
            asyncio.run(ticket_service.get_by_ticket_uid(ticket_uid))

        assert exc_info.value.ticket_uid == ticket_uid

    def test_get_all_success(self, ticket_service, mock_ticket_repository, sample_ticket):
        mock_ticket_repository.get_all.return_value = ([sample_ticket], 1)

        tickets, total = asyncio.run(ticket_service.get_all(page=1, size=10))

        mock_ticket_repository.get_all.assert_awaited_once_with(1, 10)
        assert len(tickets) == 1
        assert total == 1
        assert isinstance(tickets[0], TicketResponse)

    def test_get_by_username_success(self, ticket_service, mock_ticket_repository, sample_ticket):
        username = "testuser"
        mock_ticket_repository.get_by_username.return_value = ([sample_ticket], 1)

        tickets, total = asyncio.run(ticket_service.get_by_username(username, page=1, size=10))

        mock_ticket_repository.get_by_username.assert_awaited_once_with(username, 1, 10)
        assert len(tickets) == 1
        assert total == 1

    def test_purchase_ticket_without_bonus(
        self,
        ticket_service,
        mock_ticket_repository,
        mock_gateway_connector,
        mock_bonus_connector,
        sample_flight,
    ):
        username = "testuser"
        ticket_request = TicketCreateRequest(flightNumber="AFL031", price=1500, paidFromBalance=False)
        mock_gateway_connector.find_flight_by_number.return_value = sample_flight
        mock_ticket_repository.save_new_ticket.return_value = str(uuid.uuid4())

        result = asyncio.run(ticket_service.purchase_ticket(ticket_request, username))

        assert isinstance(result, TicketPurchaseResponse)
        assert result.flightNumber == ticket_request.flightNumber
        assert result.price == ticket_request.price
        assert result.paidByMoney == 1500
        assert result.paidByBonuses == 0
        assert result.status == TicketStatus.PAID
        mock_bonus_connector.change_user_balance.assert_awaited_once_with(username, 150)
        mock_bonus_connector.create_history_record.assert_awaited_once()

    def test_purchase_ticket_with_bonus_sufficient_balance(
        self,
        ticket_service,
        mock_ticket_repository,
        mock_gateway_connector,
        mock_bonus_connector,
        sample_flight,
    ):
        username = "testuser"
        ticket_request = TicketCreateRequest(flightNumber="AFL031", price=1500, paidFromBalance=True)
        mock_gateway_connector.find_flight_by_number.return_value = sample_flight
        mock_bonus_connector.get_user_balance.return_value = 2000
        mock_ticket_repository.save_new_ticket.return_value = str(uuid.uuid4())

        result = asyncio.run(ticket_service.purchase_ticket(ticket_request, username))

        assert isinstance(result, TicketPurchaseResponse)
        assert result.paidByMoney == 0
        assert result.paidByBonuses == 1500
        mock_bonus_connector.change_user_balance.assert_awaited_once_with(username, -1500)
        mock_bonus_connector.create_history_record.assert_awaited_once()

    def test_purchase_ticket_with_bonus_insufficient_balance(
        self,
        ticket_service,
        mock_ticket_repository,
        mock_gateway_connector,
        mock_bonus_connector,
        sample_flight,
    ):
        username = "testuser"
        ticket_request = TicketCreateRequest(flightNumber="AFL031", price=1500, paidFromBalance=True)
        mock_gateway_connector.find_flight_by_number.return_value = sample_flight
        mock_bonus_connector.get_user_balance.return_value = 500

        with pytest.raises(InsufficientBalanceError) as exc_info:
            asyncio.run(ticket_service.purchase_ticket(ticket_request, username))

        assert exc_info.value.balance == 500
        assert exc_info.value.required == 1500
        mock_ticket_repository.save_new_ticket.assert_not_awaited()

    def test_purchase_ticket_flight_not_found(
        self,
        ticket_service,
        mock_ticket_repository,
        mock_gateway_connector,
        mock_bonus_connector,
    ):
        username = "testuser"
        ticket_request = TicketCreateRequest(flightNumber="INVALID", price=1500, paidFromBalance=False)
        mock_gateway_connector.find_flight_by_number.side_effect = FlightNotFoundError("INVALID")

        with pytest.raises(FlightNotFoundError):
            asyncio.run(ticket_service.purchase_ticket(ticket_request, username))

    def test_purchase_ticket_price_mismatch(
        self,
        ticket_service,
        mock_ticket_repository,
        mock_gateway_connector,
        mock_bonus_connector,
        sample_flight,
    ):
        username = "testuser"
        ticket_request = TicketCreateRequest(flightNumber="AFL031", price=2000, paidFromBalance=False)
        mock_gateway_connector.find_flight_by_number.return_value = sample_flight

        with pytest.raises(FlightNotFoundError):
            asyncio.run(ticket_service.purchase_ticket(ticket_request, username))

    def test_cancel_ticket_success(
        self,
        ticket_service,
        mock_ticket_repository,
        mock_bonus_connector,
        sample_ticket,
    ):
        ticket_uid = str(sample_ticket.ticket_uid)
        username = "testuser"
        mock_ticket_repository.get_by_ticket_uid.return_value = sample_ticket
        mock_bonus_connector.get_user_history.return_value = []

        asyncio.run(ticket_service.cancel_ticket(ticket_uid, username))

        mock_ticket_repository.get_by_ticket_uid.assert_awaited_once_with(ticket_uid)
        mock_ticket_repository.cancel_ticket.assert_awaited_once_with(ticket_uid)

    def test_cancel_ticket_not_found(self, ticket_service, mock_ticket_repository, mock_bonus_connector):
        ticket_uid = str(uuid.uuid4())
        username = "testuser"
        mock_ticket_repository.get_by_ticket_uid.return_value = None

        with pytest.raises(TicketNotFoundError):
            asyncio.run(ticket_service.cancel_ticket(ticket_uid, username))

    def test_cancel_ticket_wrong_user(
        self, ticket_service, mock_ticket_repository, mock_bonus_connector, sample_ticket
    ):
        ticket_uid = str(sample_ticket.ticket_uid)
        username = "wronguser"
        mock_ticket_repository.get_by_ticket_uid.return_value = sample_ticket

        with pytest.raises(TicketNotFoundError):
            asyncio.run(ticket_service.cancel_ticket(ticket_uid, username))

    def test_cancel_ticket_already_canceled(
        self,
        ticket_service,
        mock_ticket_repository,
        mock_bonus_connector,
        sample_ticket,
    ):
        from app.services.enums import TicketStatus

        ticket_uid = str(sample_ticket.ticket_uid)
        username = "testuser"
        sample_ticket.status = TicketStatus.CANCELED.value
        mock_ticket_repository.get_by_ticket_uid.return_value = sample_ticket

        asyncio.run(ticket_service.cancel_ticket(ticket_uid, username))

        mock_ticket_repository.cancel_ticket.assert_not_awaited()

    def test_cancel_ticket_with_fill_in_balance_history(
        self,
        ticket_service,
        mock_ticket_repository,
        mock_bonus_connector,
        sample_ticket,
    ):
        ticket_uid = str(sample_ticket.ticket_uid)
        username = "testuser"
        mock_ticket_repository.get_by_ticket_uid.return_value = sample_ticket
        mock_bonus_connector.get_user_balance.return_value = 200
        mock_bonus_connector.get_user_history.return_value = [
            {
                "ticketUid": ticket_uid,
                "balanceDiff": 150,
                "operationType": "FILL_IN_BALANCE",
            }
        ]

        asyncio.run(ticket_service.cancel_ticket(ticket_uid, username))

        mock_bonus_connector.change_user_balance.assert_awaited_once_with(username, -150)
        mock_bonus_connector.create_history_record.assert_awaited_once()

    def test_cancel_ticket_with_debit_history(
        self,
        ticket_service,
        mock_ticket_repository,
        mock_bonus_connector,
        sample_ticket,
    ):
        ticket_uid = str(sample_ticket.ticket_uid)
        username = "testuser"
        mock_ticket_repository.get_by_ticket_uid.return_value = sample_ticket
        mock_bonus_connector.get_user_history.return_value = [
            {
                "ticketUid": ticket_uid,
                "balanceDiff": -1500,
                "operationType": "DEBIT_THE_ACCOUNT",
            }
        ]

        asyncio.run(ticket_service.cancel_ticket(ticket_uid, username))

        mock_bonus_connector.change_user_balance.assert_awaited_once_with(username, 1500)
        mock_bonus_connector.create_history_record.assert_awaited_once()
