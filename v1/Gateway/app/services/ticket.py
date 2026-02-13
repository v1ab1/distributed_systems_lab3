from app.services.bonus import BonusService
from app.presentation.api.schemas import (
    TicketResponse,
    UserInfoResponse,
    PrivilegeShortInfo,
    TicketCreateRequest,
    TicketPurchaseResponse,
)
from app.infrastructure.connectors.ticket import TicketConnector


class TicketService:
    def __init__(self, ticket_connector: TicketConnector):
        self._ticket_connector = ticket_connector

    def purchase_ticket(self, ticket: TicketCreateRequest, username: str) -> TicketPurchaseResponse:
        return self._ticket_connector.purchase_ticket(ticket, username)

    def get_user_tickets(self, username: str) -> list[TicketResponse]:
        return self._ticket_connector.get_user_tickets(username)

    def get_ticket_by_uid(self, ticket_uid: str, username: str) -> TicketResponse:
        ticket = self._ticket_connector.get_ticket_by_uid(ticket_uid)
        return ticket

    def cancel_ticket(self, ticket_uid: str, username: str) -> None:
        return self._ticket_connector.cancel_ticket(ticket_uid, username)

    def get_user_info(self, username: str, bonus_service: BonusService) -> UserInfoResponse:
        tickets = self.get_user_tickets(username)
        me_response = bonus_service.get_me(username)
        return UserInfoResponse(
            tickets=tickets,
            privilege=PrivilegeShortInfo(balance=me_response.balance, status=me_response.status),
        )
