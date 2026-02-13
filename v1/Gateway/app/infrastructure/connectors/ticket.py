import os

from datetime import datetime
from urllib.parse import urljoin

import httpx

from dotenv import load_dotenv

from app.presentation.api.schemas import (
    TicketResponse,
    AirportResponse,
    PrivilegeShortInfo,
    TicketCreateRequest,
    TicketPurchaseResponse,
)
from app.infrastructure.connectors.bonus import BonusConnector

load_dotenv(override=True)
ticket_service_url = os.getenv("TICKET_SERVICE_URL", "")
flight_service_url = os.getenv("FLIGHT_SERVICE_URL", "")


class TicketConnector:
    def __init__(self) -> None:
        self._bonus_connector = BonusConnector()

    def _get_airport(self, airport_id: int) -> AirportResponse:
        with httpx.Client(verify=False, timeout=10.0) as client:
            response = client.get(urljoin(flight_service_url, f"/v1/airports/{airport_id}"))
            response.raise_for_status()
            response_json = response.json()
            return AirportResponse.model_validate(response_json)

    def _format_airport_name(self, airport: AirportResponse) -> str:
        return f"{airport.city} {airport.name}"

    def _get_flight_info(self, flight_number: str) -> tuple[str, str, str]:
        with httpx.Client(verify=False, timeout=10.0) as client:
            response = client.get(
                urljoin(flight_service_url, "/v1/flights"),
                params={"page": 1, "size": 1000},
            )
            response.raise_for_status()
            response_json = response.json()

            for flight_item in response_json.get("items", []):
                if flight_item["flight_number"] == flight_number:
                    from_airport = self._get_airport(flight_item["from_airport_id"])
                    to_airport = self._get_airport(flight_item["to_airport_id"])
                    flight_datetime = datetime.fromisoformat(flight_item["datetime"].replace("Z", "+00:00"))
                    return (
                        self._format_airport_name(from_airport),
                        self._format_airport_name(to_airport),
                        flight_datetime.strftime("%Y-%m-%d %H:%M"),
                    )
        return ("", "", "")

    def purchase_ticket(self, ticket: TicketCreateRequest, username: str) -> TicketPurchaseResponse:
        with httpx.Client(verify=False, timeout=10.0) as client:
            response = client.post(
                urljoin(ticket_service_url, "/api/v1/tickets"),
                headers={"X-User-Name": username},
                json=ticket.model_dump(),
            )
            if response.status_code == 402:
                from fastapi import HTTPException

                error_data = response.json()
                raise HTTPException(
                    status_code=402,
                    detail=error_data.get("message", "Insufficient balance"),
                )
            response.raise_for_status()
            response_json = response.json()

            from_airport, to_airport, flight_date = self._get_flight_info(ticket.flightNumber)

            me_response = self._bonus_connector.get_me(username)

            return TicketPurchaseResponse(
                ticketUid=str(response_json["ticketUid"]),
                flightNumber=response_json["flightNumber"],
                fromAirport=from_airport,
                toAirport=to_airport,
                date=flight_date if flight_date else response_json.get("date", ""),
                price=response_json["price"],
                paidByMoney=response_json["paidByMoney"],
                paidByBonuses=response_json["paidByBonuses"],
                status=response_json["status"],
                privilege=PrivilegeShortInfo(balance=me_response.balance, status=me_response.status),
            )

    def get_user_tickets(self, username: str) -> list[TicketResponse]:
        with httpx.Client(verify=False, timeout=10.0) as client:
            response = client.get(
                urljoin(ticket_service_url, f"/api/v1/tickets/user/{username}"),
                params={"page": 1, "size": 1000},
            )
            response.raise_for_status()
            response_json = response.json()

            tickets = []
            for ticket_item in response_json.get("items", []):
                from_airport, to_airport, flight_date = self._get_flight_info(ticket_item["flight_number"])

                tickets.append(
                    TicketResponse(
                        ticketUid=str(ticket_item["ticket_uid"]),
                        flightNumber=ticket_item["flight_number"],
                        fromAirport=from_airport,
                        toAirport=to_airport,
                        date=flight_date,
                        price=ticket_item["price"],
                        status=ticket_item["status"],
                    )
                )
            return tickets

    def get_ticket_by_uid(self, ticket_uid: str) -> TicketResponse:
        with httpx.Client(verify=False, timeout=10.0) as client:
            response = client.get(
                urljoin(ticket_service_url, f"/api/v1/tickets/{ticket_uid}"),
            )
            response.raise_for_status()
            response_json = response.json()

            from_airport, to_airport, flight_date = self._get_flight_info(response_json["flight_number"])

            return TicketResponse(
                ticketUid=str(response_json["ticket_uid"]),
                flightNumber=response_json["flight_number"],
                fromAirport=from_airport,
                toAirport=to_airport,
                date=flight_date,
                price=response_json["price"],
                status=response_json["status"],
            )

    def cancel_ticket(self, ticket_uid: str, username: str) -> None:
        with httpx.Client(verify=False, timeout=10.0) as client:
            response = client.delete(
                urljoin(ticket_service_url, f"/api/v1/tickets/{ticket_uid}"),
                headers={"X-User-Name": username},
            )
            response.raise_for_status()
