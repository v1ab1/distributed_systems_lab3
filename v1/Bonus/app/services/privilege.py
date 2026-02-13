import uuid as uuid_lib

from uuid import UUID
from typing import cast
from datetime import datetime

from app.services.exceptions import UserNotFoundError, UsernameAlreadyExistError
from app.presentation.api.schemas import MeResponse, HistoryItem, PrivilegeResponse
from app.infrastructure.repositories import PrivilegeRepository


class PrivilegeService:
    def __init__(self, privilege_repository: PrivilegeRepository):
        self._privilege_repository = privilege_repository

    async def create_new_user(self, username: str) -> None:
        user = await self._privilege_repository.get_user(username)

        if user is not None:
            raise UsernameAlreadyExistError(username=username)

        await self._privilege_repository.create_new_user(username)
        return

    async def delete_user(self, username: str) -> None:
        user = await self._privilege_repository.get_user(username)

        if user is None:
            raise UserNotFoundError(username=username)

        await self._privilege_repository.delete_user(username)
        return

    async def get_user(self, username: str) -> PrivilegeResponse:
        user = await self._privilege_repository.get_user(username)

        if user is None:
            raise UserNotFoundError(username=username)

        return PrivilegeResponse.model_validate(user)

    async def set_user_balance(self, username: str, balance: int) -> None:
        user = await self._privilege_repository.get_user(username)

        if user is None:
            raise UserNotFoundError(username=username)

        await self._privilege_repository.set_balance(username, balance)

    async def change_user_balance(self, username: str, balance: int) -> None:
        user = await self._privilege_repository.get_user(username)

        if user is None:
            await self._privilege_repository.create_new_user(username)
            user = await self._privilege_repository.get_user(username)
            if user is None:
                raise UserNotFoundError(username=username)

        await self._privilege_repository.set_balance(username, int(user.balance or 0) + balance)

    async def create_history_record(
        self, username: str, ticket_uid: str, balance_diff: int, operation_type: str
    ) -> None:
        user = await self._privilege_repository.get_user(username)

        if user is None:
            await self._privilege_repository.create_new_user(username)
            user = await self._privilege_repository.get_user(username)
            if user is None:
                raise UserNotFoundError(username=username)

        ticket_uuid = uuid_lib.UUID(ticket_uid)
        await self._privilege_repository.create_history_record(username, ticket_uuid, balance_diff, operation_type)

    async def get_me(self, username: str) -> MeResponse:
        user = await self._privilege_repository.get_user(username)

        if user is None:
            await self._privilege_repository.create_new_user(username)
            user = await self._privilege_repository.get_user(username)
            if user is None:
                raise UserNotFoundError(username=username)

        history_records = await self._privilege_repository.get_user_history(username)
        history = [
            HistoryItem(
                date=cast(datetime, record.datetime),
                ticketUid=cast(UUID, record.ticket_uid),
                balanceDiff=cast(int, record.balance_diff),
                operationType=cast(str, record.operation_type),
            )
            for record in history_records
        ]

        return MeResponse(
            balance=int(user.balance) or 0,
            status=str(user.status),
            history=history,
        )
