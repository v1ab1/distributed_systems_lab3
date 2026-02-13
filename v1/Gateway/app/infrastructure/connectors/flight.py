import os

from datetime import datetime
from urllib.parse import urljoin

import httpx

from dotenv import load_dotenv

from app.presentation.api.schemas import FlightResponse, AirportResponse, AllFlightsResponse

load_dotenv(override=True)
flight_service_url = os.getenv("FLIGHT_SERVICE_URL", "")


class FlightConnector:
    def _get_airport(self, airport_id: int) -> AirportResponse:
        with httpx.Client(verify=False) as client:
            response = client.get(urljoin(flight_service_url, f"/v1/airports/{airport_id}"))
            response.raise_for_status()
            response_json = response.json()
            return AirportResponse.model_validate(response_json)

    def _format_airport_name(self, airport: AirportResponse) -> str:
        return f"{airport.city} {airport.name}"

    def get_flights(self, page: int, size: int) -> AllFlightsResponse:
        with httpx.Client(verify=False) as client:
            response = client.get(
                urljoin(flight_service_url, "/v1/flights"),
                params={"page": page, "size": size},
            )
            response.raise_for_status()
            response_json = response.json()

            flights = []
            for flight_item in response_json.get("items", []):
                from_airport = self._get_airport(flight_item["from_airport_id"])
                to_airport = self._get_airport(flight_item["to_airport_id"])

                flight_datetime = datetime.fromisoformat(flight_item["datetime"].replace("Z", "+00:00"))

                flights.append(
                    FlightResponse(
                        flightNumber=flight_item["flight_number"],
                        fromAirport=self._format_airport_name(from_airport),
                        toAirport=self._format_airport_name(to_airport),
                        date=flight_datetime.strftime("%Y-%m-%d %H:%M"),
                        price=flight_item["price"],
                    )
                )

            return AllFlightsResponse(
                page=response_json.get("page", page),
                pageSize=response_json.get("pageSize", size),
                totalElements=response_json.get("totalElements", 0),
                items=flights,
            )
