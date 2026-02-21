import httpx

from fastapi import Header, Depends, APIRouter
from fastapi.responses import JSONResponse

from app.dependencies import get_bonus_service, get_ticket_service
from app.services.bonus import BonusService
from app.services.ticket import TicketService
from app.presentation.api.schemas import UserInfoResponse
from app.infrastructure.circuit_breaker import CircuitOpenError

router = APIRouter(prefix="/v1/me")


@router.get("", response_model=None)
def get_me(
    username: str = Header(..., description="Имя пользователя", alias="X-User-Name"),
    bonus_service: BonusService = Depends(get_bonus_service),
    ticket_service: TicketService = Depends(get_ticket_service),
) -> UserInfoResponse | JSONResponse:
    try:
        return ticket_service.get_user_info(username, bonus_service)
    except (CircuitOpenError, httpx.HTTPError, httpx.RequestError):
        tickets = ticket_service.get_user_tickets(username)
        return JSONResponse(
            status_code=200,
            content={
                "tickets": [t.model_dump() for t in tickets],
                "privilege": {},
            },
        )
