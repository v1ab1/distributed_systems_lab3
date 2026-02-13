from fastapi import Header, Depends, APIRouter

from app.dependencies import get_ticket_service
from app.services.ticket import TicketService
from app.presentation.api.schemas import (
    TicketResponse,
    TicketCreateRequest,
    TicketPurchaseResponse,
)

router = APIRouter(prefix="/v1/tickets")


@router.get("")
def get_user_tickets(
    username: str = Header(..., description="Имя пользователя", alias="X-User-Name"),
    ticket_service: TicketService = Depends(get_ticket_service),
) -> list[TicketResponse]:
    return ticket_service.get_user_tickets(username)


@router.get("/{ticket_uid}")
def get_ticket_by_uid(
    ticket_uid: str,
    username: str = Header(..., description="Имя пользователя", alias="X-User-Name"),
    ticket_service: TicketService = Depends(get_ticket_service),
) -> TicketResponse:
    return ticket_service.get_ticket_by_uid(ticket_uid, username)


@router.post("", status_code=200)
def purchase_ticket(
    body: TicketCreateRequest,
    username: str = Header(..., description="Имя пользователя", alias="X-User-Name"),
    ticket_service: TicketService = Depends(get_ticket_service),
) -> TicketPurchaseResponse:
    return ticket_service.purchase_ticket(body, username)


@router.delete("/{ticket_uid}", status_code=204)
def cancel_ticket(
    ticket_uid: str,
    username: str = Header(..., description="Имя пользователя", alias="X-User-Name"),
    ticket_service: TicketService = Depends(get_ticket_service),
) -> None:
    ticket_service.cancel_ticket(ticket_uid, username)
