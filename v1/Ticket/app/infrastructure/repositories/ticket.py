import uuid

from typing import cast

from sqlalchemy import Column, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.ticket import TicketDB


class TicketRepository:
    def __init__(self, db: AsyncSession):
        self._db = db

    async def get_all(self, page: int = 1, size: int = 10) -> tuple[list[TicketDB], int]:
        count_query = select(func.count()).select_from(TicketDB)
        count_result = await self._db.execute(count_query)
        total_elements = count_result.scalar() or 0

        offset = (page - 1) * size
        query = select(TicketDB).offset(offset).limit(size)
        result = await self._db.execute(query)
        tickets = result.scalars().all()
        return list(tickets), total_elements

    async def get_by_ticket_uid(self, ticket_uid: str) -> TicketDB | None:
        ticket_uuid = uuid.UUID(ticket_uid)
        query = select(TicketDB).where(TicketDB.ticket_uid == ticket_uuid)
        result = await self._db.execute(query)
        ticket = result.scalar_one_or_none()

        return ticket

    async def get_by_username(self, username: str, page: int = 1, size: int = 10) -> tuple[list[TicketDB], int]:
        count_query = select(func.count()).select_from(TicketDB).where(TicketDB.username == username)
        count_result = await self._db.execute(count_query)
        total_elements = count_result.scalar() or 0

        offset = (page - 1) * size
        query = select(TicketDB).where(TicketDB.username == username).offset(offset).limit(size)
        result = await self._db.execute(query)
        tickets = result.scalars().all()
        return list(tickets), total_elements

    async def save_new_ticket(self, ticket: TicketDB) -> str:
        self._db.add(ticket)
        await self._db.flush()
        ticket_uid = str(ticket.ticket_uid)
        await self._db.commit()
        return ticket_uid

    async def cancel_ticket(self, ticket_uid: str) -> None:
        ticket_db = await self.get_by_ticket_uid(ticket_uid)
        if ticket_db is None:
            return
        ticket_db.status = cast(Column[str], "CANCELED")
        await self._db.commit()
        await self._db.refresh(ticket_db)
