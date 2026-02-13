from fastapi import Header, Depends, APIRouter

from app.dependencies import get_bonus_service
from app.services.bonus import BonusService
from app.presentation.api.schemas import SetBalanceRequest, CreateHistoryRequest

router = APIRouter(prefix="/v1/balance")


@router.put("", status_code=204)
def change_user_balance(
    body: SetBalanceRequest,
    username: str = Header(..., description="Имя пользователя", alias="X-User-Name"),
    bonus_service: BonusService = Depends(get_bonus_service),
) -> None:
    bonus_service.change_user_balance(username, body.balance)


@router.post("/history", status_code=204)
def create_history_record(
    body: CreateHistoryRequest,
    username: str = Header(..., description="Имя пользователя", alias="X-User-Name"),
    bonus_service: BonusService = Depends(get_bonus_service),
) -> None:
    bonus_service.create_history_record(username, body.ticketUid, body.balanceDiff, body.operationType)
