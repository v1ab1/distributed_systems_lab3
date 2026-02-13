from app.presentation.api.schemas import (
    TicketResponse,
    TicketCreateRequest,
    TicketPurchaseResponse,
    UserInfoResponse,
    PrivilegeShortInfo,
    MeResponse,
    HistoryItem,
)
from datetime import datetime


class TestTicketService:
    def test_purchase_ticket_success(self, ticket_service, mock_ticket_connector):
        ticket_request = TicketCreateRequest(
            flightNumber="AFL031",
            price=1500,
            paidFromBalance=False,
        )
        username = "test_user"
        
        expected_response = TicketPurchaseResponse(
            ticketUid="123e4567-e89b-12d3-a456-426614174000",
            flightNumber="AFL031",
            fromAirport="Санкт-Петербург Пулково",
            toAirport="Москва Шереметьево",
            date="2021-10-08 20:00",
            price=1500,
            paidByMoney=1500,
            paidByBonuses=0,
            status="PAID",
            privilege=PrivilegeShortInfo(balance=150, status="BRONZE"),
        )
        
        mock_ticket_connector.purchase_ticket.return_value = expected_response
        
        result = ticket_service.purchase_ticket(ticket_request, username)
        
        mock_ticket_connector.purchase_ticket.assert_called_once_with(ticket_request, username)
        assert isinstance(result, TicketPurchaseResponse)
        assert result.ticketUid == expected_response.ticketUid
        assert result.flightNumber == expected_response.flightNumber

    def test_get_user_tickets_success(self, ticket_service, mock_ticket_connector):
        username = "test_user"
        
        expected_tickets = [
            TicketResponse(
                ticketUid="123e4567-e89b-12d3-a456-426614174000",
                flightNumber="AFL031",
                fromAirport="Санкт-Петербург Пулково",
                toAirport="Москва Шереметьево",
                date="2021-10-08 20:00",
                price=1500,
                status="PAID",
            )
        ]
        
        mock_ticket_connector.get_user_tickets.return_value = expected_tickets
        
        result = ticket_service.get_user_tickets(username)
        
        mock_ticket_connector.get_user_tickets.assert_called_once_with(username)
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0].ticketUid == expected_tickets[0].ticketUid

    def test_get_ticket_by_uid_success(self, ticket_service, mock_ticket_connector):
        ticket_uid = "123e4567-e89b-12d3-a456-426614174000"
        username = "test_user"
        
        expected_ticket = TicketResponse(
            ticketUid=ticket_uid,
            flightNumber="AFL031",
            fromAirport="Санкт-Петербург Пулково",
            toAirport="Москва Шереметьево",
            date="2021-10-08 20:00",
            price=1500,
            status="PAID",
        )
        
        mock_ticket_connector.get_ticket_by_uid.return_value = expected_ticket
        
        result = ticket_service.get_ticket_by_uid(ticket_uid, username)
        
        mock_ticket_connector.get_ticket_by_uid.assert_called_once_with(ticket_uid)
        assert isinstance(result, TicketResponse)
        assert result.ticketUid == ticket_uid

    def test_cancel_ticket_success(self, ticket_service, mock_ticket_connector):
        ticket_uid = "123e4567-e89b-12d3-a456-426614174000"
        username = "test_user"
        
        mock_ticket_connector.cancel_ticket.return_value = None
        
        result = ticket_service.cancel_ticket(ticket_uid, username)
        
        mock_ticket_connector.cancel_ticket.assert_called_once_with(ticket_uid, username)
        assert result is None

    def test_get_user_info_success(self, ticket_service, mock_ticket_connector, bonus_service, mock_bonus_connector):
        username = "test_user"
        
        expected_tickets = [
            TicketResponse(
                ticketUid="123e4567-e89b-12d3-a456-426614174000",
                flightNumber="AFL031",
                fromAirport="Санкт-Петербург Пулково",
                toAirport="Москва Шереметьево",
                date="2021-10-08 20:00",
                price=1500,
                status="PAID",
            )
        ]
        
        expected_me_response = MeResponse(
            balance=150,
            status="BRONZE",
            history=[
                HistoryItem(
                    date=datetime(2021, 10, 8, 19, 59, 19),
                    ticketUid="123e4567-e89b-12d3-a456-426614174000",
                    balanceDiff=150,
                    operationType="FILL_IN_BALANCE",
                )
            ],
        )
        
        mock_ticket_connector.get_user_tickets.return_value = expected_tickets
        mock_bonus_connector.get_me.return_value = expected_me_response
        
        result = ticket_service.get_user_info(username, bonus_service)
        
        mock_ticket_connector.get_user_tickets.assert_called_once_with(username)
        mock_bonus_connector.get_me.assert_called_once_with(username)
        assert isinstance(result, UserInfoResponse)
        assert len(result.tickets) == 1
        assert result.privilege.balance == 150
        assert result.privilege.status == "BRONZE"
