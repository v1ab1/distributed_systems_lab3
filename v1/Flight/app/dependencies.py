from app.services import FlightService, AirportService
from app.db.engine import get_db
from app.infrastructure.repositories import FlightRepository, AirportRepository


async def get_airport_service() -> AirportService:  # type: ignore
    async for session in get_db():
        airport_repository = AirportRepository(session)

        return AirportService(airport_repository)


async def get_flight_service() -> FlightService:  # type: ignore
    async for session in get_db():
        flight_repository = FlightRepository(session)

        return FlightService(flight_repository)
