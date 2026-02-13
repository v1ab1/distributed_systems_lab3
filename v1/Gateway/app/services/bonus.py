from app.presentation.api.schemas import (
    MeResponse,
    PrivilegeInfoResponse,
)
from app.infrastructure.connectors.bonus import BonusConnector


class BonusService:
    def __init__(self, bonus_connector: BonusConnector):
        self._bonus_connector = bonus_connector

    def get_me(self, username: str) -> MeResponse:
        return self._bonus_connector.get_me(username)

    def get_privilege_info(self, username: str) -> PrivilegeInfoResponse:
        me_response = self._bonus_connector.get_me(username)
        return PrivilegeInfoResponse(
            balance=me_response.balance,
            status=me_response.status,
            history=me_response.history,
        )

    def get_user_balance(self, username: str) -> int:
        return self._bonus_connector.get_user_balance(username)

    def change_user_balance(self, username: str, balance_diff: int) -> None:
        self._bonus_connector.change_user_balance(username, balance_diff)

    def create_history_record(self, username: str, ticket_uid: str, balance_diff: int, operation_type: str) -> None:
        self._bonus_connector.create_history_record(username, ticket_uid, balance_diff, operation_type)
