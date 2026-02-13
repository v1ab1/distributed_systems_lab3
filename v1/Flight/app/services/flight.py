from datetime import UTC, datetime

from app.db.models.flight import FlightDB
from app.services.exceptions import FlightNotFoundError
from app.presentation.api.schemas import FlightMeta, FlightResponse
from app.infrastructure.repositories.flight import FlightRepository


class FlightService:
    def __init__(self, flight_repository: FlightRepository):
        self._flight_repository = flight_repository

    async def get_by_id(self, flight_id: int) -> FlightResponse:
        flight_db = await self._flight_repository.get_by_id(flight_id)
        if flight_db is None:
            raise FlightNotFoundError(flight_id)
        flight = FlightResponse.model_validate(flight_db)
        return flight

    async def get_all(self, page: int = 1, size: int = 10) -> tuple[list[FlightResponse], int]:
        flights_db, total_elements = await self._flight_repository.get_all(page, size)
        flights = [FlightResponse.model_validate(flight) for flight in flights_db]
        return flights, total_elements

    async def save_new_flight(self, flight: FlightMeta) -> int:
        flight_data = flight.model_dump()
        flight_data["datetime"] = datetime.now(UTC)
        flight_db = FlightDB(**flight_data)
        return await self._flight_repository.save_new_flight(flight_db)

    async def update_flight(self, flight_id: int, flight: FlightMeta) -> None:
        flight_db = await self._flight_repository.get_by_id(flight_id)
        if flight_db is None:
            raise FlightNotFoundError(flight_id)
        await self._flight_repository.update_flight(flight_id, flight)

    async def delete_flight(self, flight_id: int) -> None:
        flight_db = await self._flight_repository.get_by_id(flight_id)
        if flight_db is None:
            raise FlightNotFoundError(flight_id)
        await self._flight_repository.delete_flight(flight_id)
