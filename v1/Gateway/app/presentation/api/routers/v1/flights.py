from fastapi import Depends, APIRouter

from app.dependencies import get_flight_service
from app.services.flight import FlightService
from app.presentation.api.schemas import PaginationResponse

router = APIRouter(prefix="/v1/flights")


@router.get("")
def get_all_flights(
    page: int = 1,
    size: int = 10,
    flight_service: FlightService = Depends(get_flight_service),
) -> PaginationResponse:
    flights = flight_service.get_all(page, size)
    return flights
