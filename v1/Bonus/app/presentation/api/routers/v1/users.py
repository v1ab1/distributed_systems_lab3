from fastapi import Header, Depends, APIRouter

from app.dependencies import get_privilege_service
from app.services.privilege import PrivilegeService
from app.presentation.api.schemas import PrivilegeResponse

router = APIRouter(prefix="/v1/users")


@router.get("")
async def get_user(
    username: str = Header(..., description="Имя пользователя", alias="X-User-Name"),
    privilege_service: PrivilegeService = Depends(get_privilege_service),
) -> PrivilegeResponse:
    user = await privilege_service.get_user(username)
    return user


@router.post("", status_code=204)
async def create_user(
    username: str = Header(..., description="Имя пользователя", alias="X-User-Name"),
    privilege_service: PrivilegeService = Depends(get_privilege_service),
) -> None:
    await privilege_service.create_new_user(username)
    return


@router.delete("", status_code=204)
async def delete_user(
    username: str = Header(..., description="Имя пользователя", alias="X-User-Name"),
    privilege_service: PrivilegeService = Depends(get_privilege_service),
) -> None:
    await privilege_service.delete_user(username)
    return
