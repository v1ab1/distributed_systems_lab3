from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.airport import AirportDB
from app.presentation.api.schemas import AirportMeta


class AirportRepository:
    def __init__(self, db: AsyncSession):
        self._db = db

    async def get_all(self) -> list[AirportDB]:
        query = select(AirportDB)
        result = await self._db.execute(query)
        airports = result.scalars().all()
        return list(airports)

    async def get_by_id(self, id: int) -> AirportDB | None:
        query = select(AirportDB).where(AirportDB.id == id)
        result = await self._db.execute(query)
        airport = result.scalar_one_or_none()

        return airport

    async def save_new_airport(self, airport: AirportDB) -> int:
        self._db.add(airport)
        await self._db.flush()
        person_id = airport.id
        await self._db.commit()
        return int(person_id)

    async def delete_airport(self, airport_id: int) -> None:
        await self.get_by_id(airport_id)
        await self._db.execute(delete(AirportDB).where(AirportDB.id == airport_id))
        await self._db.commit()

    async def update_airport(self, airport_id: int, airport: AirportMeta) -> None:
        airport_db = await self.get_by_id(airport_id)
        for key, value in airport.model_dump(exclude_unset=True).items():
            setattr(airport_db, key, value)
        await self._db.commit()
        await self._db.refresh(airport_db)
