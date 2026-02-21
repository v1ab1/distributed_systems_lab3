import httpx

from fastapi import Header, Depends, APIRouter, HTTPException
from fastapi.responses import JSONResponse

from app.dependencies import get_ticket_service
from app.services.ticket import TicketService
from app.presentation.api.schemas import (
    TicketResponse,
    TicketCreateRequest,
    TicketPurchaseResponse,
)
from app.infrastructure.circuit_breaker import CircuitOpenError

router = APIRouter(prefix="/v1/tickets")


@router.get("", response_model=None)
def get_user_tickets(
    username: str = Header(..., description="Имя пользователя", alias="X-User-Name"),
    ticket_service: TicketService = Depends(get_ticket_service),
) -> list[TicketResponse] | JSONResponse:
    try:
        return ticket_service.get_user_tickets(username)
    except (CircuitOpenError, httpx.HTTPError, httpx.RequestError):
        return JSONResponse(
            status_code=503,
            content={"message": "Ticket service unavailable"},
        )


@router.get("/{ticket_uid}", response_model=None)
def get_ticket_by_uid(
    ticket_uid: str,
    username: str = Header(..., description="Имя пользователя", alias="X-User-Name"),
    ticket_service: TicketService = Depends(get_ticket_service),
) -> TicketResponse | JSONResponse:
    try:
        return ticket_service.get_ticket_by_uid(ticket_uid, username)
    except (CircuitOpenError, httpx.HTTPError, httpx.RequestError):
        return JSONResponse(
            status_code=503,
            content={"message": "Ticket service unavailable"},
        )


@router.post("", status_code=200, response_model=None)
def purchase_ticket(
    body: TicketCreateRequest,
    username: str = Header(..., description="Имя пользователя", alias="X-User-Name"),
    ticket_service: TicketService = Depends(get_ticket_service),
) -> TicketPurchaseResponse | JSONResponse:
    try:
        return ticket_service.purchase_ticket(body, username)
    except (CircuitOpenError, httpx.HTTPError, httpx.RequestError):
        return JSONResponse(
            status_code=503,
            content={"message": "Bonus Service unavailable"},
        )
    except Exception:
        return JSONResponse(
            status_code=503,
            content={"message": "Bonus Service unavailable"},
        )


@router.delete("/{ticket_uid}", status_code=204)
def cancel_ticket(
    ticket_uid: str,
    username: str = Header(..., description="Имя пользователя", alias="X-User-Name"),
    ticket_service: TicketService = Depends(get_ticket_service),
) -> None:
    try:
        ticket_service.cancel_ticket(ticket_uid, username)
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise HTTPException(status_code=404, detail="Ticket not found") from e
        from app.infrastructure.refund_queue import enqueue_refund

        enqueue_refund(ticket_uid, username)
    except (CircuitOpenError, httpx.HTTPError, httpx.RequestError):
        from app.infrastructure.refund_queue import enqueue_refund

        enqueue_refund(ticket_uid, username)
