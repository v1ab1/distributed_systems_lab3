import uuid

from typing import cast
from datetime import datetime

from sqlalchemy import Column, delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.privilege import PrivilegeDB
from app.db.models.privilege_history import PrivilegeHistoryDB


class PrivilegeRepository:
    def __init__(self, db: AsyncSession):
        self._db = db

    async def create_new_user(self, username: str) -> int:
        person_db = PrivilegeDB(username=username)
        self._db.add(person_db)
        await self._db.flush()
        person_id = person_db.id
        await self._db.commit()
        return int(person_id)

    async def get_user(self, username: str) -> PrivilegeDB | None:
        query = select(PrivilegeDB).where(PrivilegeDB.username == username)
        result = await self._db.execute(query)
        person = result.scalar_one_or_none()

        return person

    async def delete_user(self, username: str) -> None:
        await self._db.execute(delete(PrivilegeDB).where(PrivilegeDB.username == username))
        await self._db.commit()

    async def set_balance(self, username: str, balance: int) -> None:
        user = await self.get_user(username)
        if user is None:
            return
        user.balance = cast(Column[int], balance)
        await self._db.commit()
        await self._db.refresh(user)

    async def create_history_record(
        self, username: str, ticket_uid: uuid.UUID, balance_diff: int, operation_type: str
    ) -> None:
        user = await self.get_user(username)
        if user is None:
            return
        history_record = PrivilegeHistoryDB(
            privilege_id=user.id,
            ticket_uid=ticket_uid,
            datetime=datetime.now(),
            balance_diff=balance_diff,
            operation_type=operation_type,
        )
        self._db.add(history_record)
        await self._db.commit()

    async def get_user_history(self, username: str) -> list[PrivilegeHistoryDB]:
        user = await self.get_user(username)
        if user is None:
            return []
        query = select(PrivilegeHistoryDB).where(PrivilegeHistoryDB.privilege_id == user.id)
        result = await self._db.execute(query)
        history = result.scalars().all()
        return list(history)
