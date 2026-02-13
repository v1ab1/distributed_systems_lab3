import os

from uuid import UUID
from typing import Any
from urllib.parse import urljoin

import httpx

from dotenv import load_dotenv

load_dotenv(override=True)
gateway_service_url = os.getenv("GATEWAY_SERVICE_URL", "")


class BonusConnector:
    async def get_user_balance(self, username: str) -> int:
        async with httpx.AsyncClient(verify=False, timeout=10.0) as client:
            response = await client.get(
                urljoin(gateway_service_url, "/api/v1/me"),
                headers={"X-User-Name": username},
            )
            response.raise_for_status()
            response_json = response.json()
            return response_json.get("balance", 0) or 0

    async def change_user_balance(self, username: str, balance_diff: int) -> None:
        async with httpx.AsyncClient(verify=False, timeout=10.0) as client:
            response = await client.put(
                urljoin(gateway_service_url, "/api/v1/balance"),
                headers={"X-User-Name": username},
                json={"balance": balance_diff},
            )
            response.raise_for_status()

    async def create_history_record(
        self,
        username: str,
        ticket_uid: UUID,
        balance_diff: int,
        operation_type: str,
    ) -> None:
        async with httpx.AsyncClient(verify=False, timeout=10.0) as client:
            response = await client.post(
                urljoin(gateway_service_url, "/api/v1/balance/history"),
                headers={"X-User-Name": username},
                json={
                    "ticketUid": str(ticket_uid),
                    "balanceDiff": balance_diff,
                    "operationType": operation_type,
                },
            )
            response.raise_for_status()

    async def get_user_history(self, username: str) -> list[dict[str, Any]]:
        async with httpx.AsyncClient(verify=False, timeout=10.0) as client:
            response = await client.get(
                urljoin(gateway_service_url, "/api/v1/me"),
                headers={"X-User-Name": username},
            )
            response.raise_for_status()
            response_json = response.json()
            return response_json.get("history", [])  # type: ignore
