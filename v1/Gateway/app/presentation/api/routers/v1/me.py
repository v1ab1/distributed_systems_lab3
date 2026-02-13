from fastapi import Header, Depends, APIRouter

from app.dependencies import get_bonus_service, get_ticket_service
from app.services.bonus import BonusService
from app.services.ticket import TicketService
from app.presentation.api.schemas import UserInfoResponse

router = APIRouter(prefix="/v1/me")


@router.get("")
def get_me(
    username: str = Header(..., description="Имя пользователя", alias="X-User-Name"),
    bonus_service: BonusService = Depends(get_bonus_service),
    ticket_service: TicketService = Depends(get_ticket_service),
) -> UserInfoResponse:
    return ticket_service.get_user_info(username, bonus_service)
