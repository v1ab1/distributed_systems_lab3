import os

from urllib.parse import urljoin

import httpx

from dotenv import load_dotenv

from app.presentation.api.schemas import MeResponse

load_dotenv(override=True)
bonus_service_url = os.getenv("BONUS_SERVICE_URL", "")


class BonusConnector:
    def get_me(self, username: str) -> MeResponse:
        with httpx.Client(verify=False, timeout=10.0) as client:
            response = client.get(
                urljoin(bonus_service_url, "/api/v1/me"),
                headers={"X-User-Name": username},
            )
            response.raise_for_status()
            response_json = response.json()
            return MeResponse.model_validate(response_json)

    def get_user_balance(self, username: str) -> int:
        me_response = self.get_me(username)
        return me_response.balance

    def change_user_balance(self, username: str, balance_diff: int) -> None:
        with httpx.Client(verify=False, timeout=10.0) as client:
            response = client.put(
                urljoin(bonus_service_url, "/api/v1/balance"),
                headers={"X-User-Name": username},
                json={"balance": balance_diff},
            )
            response.raise_for_status()

    def create_history_record(
        self,
        username: str,
        ticket_uid: str,
        balance_diff: int,
        operation_type: str,
    ) -> None:
        with httpx.Client(verify=False, timeout=10.0) as client:
            response = client.post(
                urljoin(bonus_service_url, "/api/v1/balance/history"),
                headers={"X-User-Name": username},
                json={
                    "ticketUid": ticket_uid,
                    "balanceDiff": balance_diff,
                    "operationType": operation_type,
                },
            )
            response.raise_for_status()
