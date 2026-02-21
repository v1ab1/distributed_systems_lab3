import httpx

from fastapi import Depends, APIRouter
from fastapi.responses import JSONResponse

from app.dependencies import get_flight_service
from app.services.flight import FlightService
from app.presentation.api.schemas import PaginationResponse
from app.infrastructure.circuit_breaker import CircuitOpenError

router = APIRouter(prefix="/v1/flights")


@router.get("", response_model=None)
def get_all_flights(
    page: int = 1,
    size: int = 10,
    flight_service: FlightService = Depends(get_flight_service),
) -> PaginationResponse | JSONResponse:
    try:
        return flight_service.get_all(page, size)
    except (CircuitOpenError, httpx.HTTPError, httpx.RequestError):
        return JSONResponse(
            status_code=503,
            content={"message": "Flight service unavailable"},
        )
