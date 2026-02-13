import os

from urllib.parse import urljoin

import httpx

from dotenv import load_dotenv

from app.services.exceptions import FlightNotFoundError
from app.presentation.api.schemas import (
    GatewayFlightResponse,
    GatewayAllFlightsResponse,
)

load_dotenv(override=True)
gateway_service_url = os.getenv("GATEWAY_SERVICE_URL", "")


class GatewayConnector:
    async def get_flights(self, page: int = 1, size: int = 10) -> GatewayAllFlightsResponse:
        async with httpx.AsyncClient(verify=False, timeout=10.0) as client:
            response = await client.get(
                urljoin(gateway_service_url, "/api/v1/flights"),
                params={"page": page, "size": size},
            )
            response.raise_for_status()
            response_json = response.json()
            return GatewayAllFlightsResponse.model_validate(response_json)

    async def find_flight_by_number(self, flight_number: str) -> GatewayFlightResponse:
        page = 1
        size = 100
        while True:
            flights_response = await self.get_flights(page, size)
            for flight in flights_response.items:
                if flight.flightNumber == flight_number:
                    return flight
            if page * size >= flights_response.totalElements:
                break
            page += 1
        raise FlightNotFoundError(flight_number)
