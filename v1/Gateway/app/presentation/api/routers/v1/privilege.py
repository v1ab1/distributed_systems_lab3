from fastapi import Header, Depends, APIRouter

from app.dependencies import get_bonus_service
from app.services.bonus import BonusService
from app.presentation.api.schemas import PrivilegeInfoResponse

router = APIRouter(prefix="/v1/privilege")


@router.get("")
def get_privilege(
    username: str = Header(..., description="Имя пользователя", alias="X-User-Name"),
    bonus_service: BonusService = Depends(get_bonus_service),
) -> PrivilegeInfoResponse:
    return bonus_service.get_privilege_info(username)
