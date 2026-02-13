from sqlalchemy import func, delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.flight import FlightDB
from app.presentation.api.schemas import FlightMeta


class FlightRepository:
    def __init__(self, db: AsyncSession):
        self._db = db

    async def get_all(self, page: int = 1, size: int = 10) -> tuple[list[FlightDB], int]:
        count_query = select(func.count()).select_from(FlightDB)
        count_result = await self._db.execute(count_query)
        total_elements = count_result.scalar() or 0

        offset = (page - 1) * size
        query = select(FlightDB).offset(offset).limit(size)
        result = await self._db.execute(query)
        flights = result.scalars().all()
        return list(flights), total_elements

    async def get_by_id(self, id: int) -> FlightDB | None:
        query = select(FlightDB).where(FlightDB.id == id)
        result = await self._db.execute(query)
        flight = result.scalar_one_or_none()

        return flight

    async def save_new_flight(self, flight: FlightDB) -> int:
        self._db.add(flight)
        await self._db.flush()
        person_id = flight.id
        await self._db.commit()
        return int(person_id)

    async def delete_flight(self, flight_id: int) -> None:
        await self.get_by_id(flight_id)
        await self._db.execute(delete(FlightDB).where(FlightDB.id == flight_id))
        await self._db.commit()

    async def update_flight(self, flight_id: int, flight: FlightMeta) -> None:
        flight_db = await self.get_by_id(flight_id)
        for key, value in flight.model_dump(exclude_unset=True).items():
            setattr(flight_db, key, value)
        await self._db.commit()
        await self._db.refresh(flight_db)
