from fastapi import Depends, Response, APIRouter

from app.dependencies import get_airport_service
from app.services.airport import AirportService
from app.presentation.api.schemas import (
    AirportMeta,
    AirportResponse,
    AllAirportsResponse,
)

router = APIRouter(prefix="/v1/airports")


@router.get("")
async def get_all_airports(
    airport_service: AirportService = Depends(get_airport_service),
) -> AllAirportsResponse:
    airports = await airport_service.get_all()
    return AllAirportsResponse(airports=airports)


@router.post("", status_code=201)
async def save_new_airport(
    body: AirportMeta,
    response: Response,
    airport_service: AirportService = Depends(get_airport_service),
) -> None:
    airport_id = await airport_service.save_new_airport(body)
    response.headers["Location"] = f"/api/v1/airports/{airport_id}"
    return None


@router.get("/{airport_id}")
async def get_airport_by_id(
    airport_id: int,
    airport_service: AirportService = Depends(get_airport_service),
) -> AirportResponse | None:
    return await airport_service.get_by_id(airport_id)


@router.patch("/{airport_id}", status_code=200)
async def update_airport_by_id(
    airport_id: int,
    body: AirportMeta,
    airport_service: AirportService = Depends(get_airport_service),
) -> None:
    await airport_service.update_airport(airport_id, body)


@router.delete("/{airport_id}", status_code=204)
async def delete_airport_by_id(
    airport_id: int,
    airport_service: AirportService = Depends(get_airport_service),
) -> None:
    await airport_service.delete_airport(airport_id)
