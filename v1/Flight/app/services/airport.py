from app.db.models.airport import AirportDB
from app.services.exceptions import AirportNotFoundError
from app.presentation.api.schemas import AirportMeta, AirportResponse
from app.infrastructure.repositories.airport import AirportRepository


class AirportService:
    def __init__(self, airport_repository: AirportRepository):
        self._airport_repository = airport_repository

    async def get_by_id(self, id: int) -> AirportResponse:
        airport_db = await self._airport_repository.get_by_id(id)
        if airport_db is None:
            raise AirportNotFoundError(id)
        airport = AirportResponse.model_validate(airport_db)
        return airport

    async def get_all(self) -> list[AirportResponse]:
        airports_db = await self._airport_repository.get_all()
        airports = [AirportResponse.model_validate(person) for person in airports_db]
        return airports

    async def save_new_airport(self, airport: AirportMeta) -> int:
        airport_db = AirportDB(**airport.model_dump())
        return await self._airport_repository.save_new_airport(airport_db)

    async def update_airport(self, id: int, airport: AirportMeta) -> None:
        airport_db = await self._airport_repository.get_by_id(id)
        if airport_db is None:
            raise AirportNotFoundError(id)
        await self._airport_repository.update_airport(id, airport)

    async def delete_airport(self, id: int) -> None:
        airport_db = await self._airport_repository.get_by_id(id)
        if airport_db is None:
            raise AirportNotFoundError(id)
        await self._airport_repository.delete_airport(id)
