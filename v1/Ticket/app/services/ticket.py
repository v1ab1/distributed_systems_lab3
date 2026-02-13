import uuid

from datetime import UTC, datetime

from app.services.enums import TicketStatus
from app.db.models.ticket import TicketDB
from app.services.exceptions import TicketNotFoundError, InsufficientBalanceError
from app.presentation.api.schemas import (
    TicketResponse,
    TicketCreateRequest,
    TicketPurchaseResponse,
    GatewayAllFlightsResponse,
)
from app.infrastructure.connectors.bonus import BonusConnector
from app.infrastructure.connectors.gateway import GatewayConnector
from app.infrastructure.repositories.ticket import TicketRepository


class TicketService:
    def __init__(
        self,
        ticket_repository: TicketRepository,
        gateway_connector: GatewayConnector,
        bonus_connector: BonusConnector,
    ):
        self._ticket_repository = ticket_repository
        self._gateway_connector = gateway_connector
        self._bonus_connector = bonus_connector

    async def get_by_ticket_uid(self, ticket_uid: str) -> TicketResponse:
        ticket_db = await self._ticket_repository.get_by_ticket_uid(ticket_uid)
        if ticket_db is None:
            raise TicketNotFoundError(ticket_uid)
        ticket = TicketResponse.model_validate(ticket_db)
        return ticket

    async def get_all(self, page: int = 1, size: int = 10) -> tuple[list[TicketResponse], int]:
        tickets_db, total_elements = await self._ticket_repository.get_all(page, size)
        tickets = [TicketResponse.model_validate(ticket) for ticket in tickets_db]
        return tickets, total_elements

    async def get_by_username(self, username: str, page: int = 1, size: int = 10) -> tuple[list[TicketResponse], int]:
        tickets_db, total_elements = await self._ticket_repository.get_by_username(username, page, size)
        tickets = [TicketResponse.model_validate(ticket) for ticket in tickets_db]
        return tickets, total_elements

    async def purchase_ticket(self, ticket: TicketCreateRequest, username: str) -> TicketPurchaseResponse:
        flight = await self._gateway_connector.find_flight_by_number(ticket.flightNumber)

        if flight.price != ticket.price:
            from app.services.exceptions import FlightNotFoundError

            raise FlightNotFoundError(ticket.flightNumber)

        ticket_uid = uuid.uuid4()
        paid_by_bonuses = 0
        paid_by_money = ticket.price

        if ticket.paidFromBalance:
            user_balance = await self._bonus_connector.get_user_balance(username)

            if user_balance < ticket.price:
                raise InsufficientBalanceError(user_balance, ticket.price)

            paid_by_bonuses = ticket.price
            paid_by_money = 0

            await self._bonus_connector.change_user_balance(username, -paid_by_bonuses)
            await self._bonus_connector.create_history_record(
                username, ticket_uid, -paid_by_bonuses, "DEBIT_THE_ACCOUNT"
            )
        else:
            bonus_amount = int(ticket.price * 0.1)
            if bonus_amount > 0:
                await self._bonus_connector.change_user_balance(username, bonus_amount)
                await self._bonus_connector.create_history_record(username, ticket_uid, bonus_amount, "FILL_IN_BALANCE")

        ticket_data = {
            "username": username,
            "flight_number": ticket.flightNumber,
            "price": ticket.price,
            "status": TicketStatus.PAID.value,
            "ticket_uid": ticket_uid,
        }
        ticket_db = TicketDB(**ticket_data)
        await self._ticket_repository.save_new_ticket(ticket_db)

        return TicketPurchaseResponse(
            ticketUid=ticket_uid,
            flightNumber=ticket.flightNumber,
            price=ticket.price,
            paidByMoney=paid_by_money,
            paidByBonuses=paid_by_bonuses,
            status=TicketStatus.PAID,
            date=datetime.now(UTC),
        )

    async def cancel_ticket(self, ticket_uid: str, username: str) -> None:
        ticket_db = await self._ticket_repository.get_by_ticket_uid(ticket_uid)
        if ticket_db is None:
            raise TicketNotFoundError(ticket_uid)

        if ticket_db.username != username:
            raise TicketNotFoundError(ticket_uid)

        if ticket_db.status == TicketStatus.CANCELED.value:
            return

        history = await self._bonus_connector.get_user_history(username)

        ticket_uuid = uuid.UUID(ticket_uid)
        ticket_history = None
        for record in history:
            record_ticket_uid = record.get("ticketUid")
            if str(record_ticket_uid) == str(ticket_uuid) or str(record_ticket_uid) == ticket_uid:
                ticket_history = record
                break

        if ticket_history:
            operation_type = ticket_history.get("operationType")
            balance_diff = ticket_history.get("balanceDiff", 0)

            if operation_type == "FILL_IN_BALANCE":
                user_balance = await self._bonus_connector.get_user_balance(username)
                amount_to_debit = min(balance_diff, user_balance)
                if amount_to_debit > 0:
                    await self._bonus_connector.change_user_balance(username, -amount_to_debit)
                    await self._bonus_connector.create_history_record(
                        username, ticket_uuid, -amount_to_debit, "DEBIT_THE_ACCOUNT"
                    )
            elif operation_type == "DEBIT_THE_ACCOUNT":
                amount_to_return = abs(balance_diff)
                await self._bonus_connector.change_user_balance(username, amount_to_return)
                await self._bonus_connector.create_history_record(
                    username, ticket_uuid, amount_to_return, "FILL_IN_BALANCE"
                )

        await self._ticket_repository.cancel_ticket(ticket_uid)

    async def get_flights(self, page: int = 1, size: int = 10) -> GatewayAllFlightsResponse:
        return await self._gateway_connector.get_flights(page, size)
