from uuid import UUID

from fastapi import Header, Depends, Response, APIRouter

from app.dependencies import get_ticket_service
from app.services.ticket import TicketService
from app.presentation.api.schemas import (
    TicketResponse,
    AllTicketsResponse,
    TicketCreateRequest,
    TicketPurchaseResponse,
)

router = APIRouter(prefix="/v1/tickets")


@router.get("")
async def get_all_tickets(
    page: int = 1,
    size: int = 10,
    ticket_service: TicketService = Depends(get_ticket_service),
) -> AllTicketsResponse:
    tickets, total_elements = await ticket_service.get_all(page, size)
    return AllTicketsResponse(page=page, pageSize=size, totalElements=total_elements, items=tickets)


@router.post("", status_code=201)
async def purchase_ticket(
    body: TicketCreateRequest,
    response: Response,
    username: str = Header(..., description="Имя пользователя", alias="X-User-Name"),
    ticket_service: TicketService = Depends(get_ticket_service),
) -> TicketPurchaseResponse:
    result = await ticket_service.purchase_ticket(body, username)
    response.headers["Location"] = f"/api/v1/tickets/{result.ticketUid}"
    return result


@router.get("/{ticket_uid}")
async def get_ticket_by_uid(
    ticket_uid: UUID,
    ticket_service: TicketService = Depends(get_ticket_service),
) -> TicketResponse:
    return await ticket_service.get_by_ticket_uid(str(ticket_uid))


@router.get("/user/{username}")
async def get_tickets_by_username(
    username: str,
    page: int = 1,
    size: int = 10,
    ticket_service: TicketService = Depends(get_ticket_service),
) -> AllTicketsResponse:
    tickets, total_elements = await ticket_service.get_by_username(username, page, size)
    return AllTicketsResponse(page=page, pageSize=size, totalElements=total_elements, items=tickets)


@router.delete("/{ticket_uid}", status_code=204)
async def cancel_ticket_by_uid(
    ticket_uid: UUID,
    username: str = Header(..., description="Имя пользователя", alias="X-User-Name"),
    ticket_service: TicketService = Depends(get_ticket_service),
) -> None:
    await ticket_service.cancel_ticket(str(ticket_uid), username)
