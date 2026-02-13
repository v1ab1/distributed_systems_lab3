from fastapi import Depends, Response, APIRouter

from app.dependencies import get_flight_service
from app.services.flight import FlightService
from app.presentation.api.schemas import (
    FlightMeta,
    FlightResponse,
    AllFlightsResponse,
)

router = APIRouter(prefix="/v1/flights")


@router.get("")
async def get_all_flights(
    page: int = 1,
    size: int = 10,
    flight_service: FlightService = Depends(get_flight_service),
) -> AllFlightsResponse:
    flights, total_elements = await flight_service.get_all(page, size)
    return AllFlightsResponse(page=page, pageSize=size, totalElements=total_elements, items=flights)


@router.post("", status_code=201)
async def save_new_flight(
    body: FlightMeta,
    response: Response,
    flight_service: FlightService = Depends(get_flight_service),
) -> None:
    flight_id = await flight_service.save_new_flight(body)
    response.headers["Location"] = f"/api/v1/flights/{flight_id}"
    return None


@router.get("/{flight_id}")
async def get_flight_by_id(
    flight_id: int,
    flight_service: FlightService = Depends(get_flight_service),
) -> FlightResponse | None:
    return await flight_service.get_by_id(flight_id)


@router.patch("/{flight_id}", status_code=200)
async def update_flight_by_id(
    flight_id: int,
    body: FlightMeta,
    flight_service: FlightService = Depends(get_flight_service),
) -> None:
    await flight_service.update_flight(flight_id, body)


@router.delete("/{flight_id}", status_code=204)
async def delete_flight_by_id(
    flight_id: int,
    flight_service: FlightService = Depends(get_flight_service),
) -> None:
    await flight_service.delete_flight(flight_id)
