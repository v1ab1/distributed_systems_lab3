from fastapi import Header, Depends, APIRouter

from app.dependencies import get_privilege_service
from app.services.privilege import PrivilegeService
from app.presentation.api.schemas import MeResponse

router = APIRouter(prefix="/v1/me")


@router.get("")
async def get_me(
    username: str = Header(..., description="Имя пользователя", alias="X-User-Name"),
    privilege_service: PrivilegeService = Depends(get_privilege_service),
) -> MeResponse:
    return await privilege_service.get_me(username)
