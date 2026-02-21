import httpx

from fastapi import Header, Depends, APIRouter
from fastapi.responses import JSONResponse

from app.dependencies import get_bonus_service
from app.services.bonus import BonusService
from app.presentation.api.schemas import PrivilegeInfoResponse
from app.infrastructure.circuit_breaker import CircuitOpenError

router = APIRouter(prefix="/v1/privilege")


@router.get("", response_model=None)
def get_privilege(
    username: str = Header(..., description="Имя пользователя", alias="X-User-Name"),
    bonus_service: BonusService = Depends(get_bonus_service),
) -> PrivilegeInfoResponse | JSONResponse:
    try:
        return bonus_service.get_privilege_info(username)
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
