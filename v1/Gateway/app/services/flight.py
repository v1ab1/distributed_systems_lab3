from app.presentation.api.schemas import AllFlightsResponse
from app.infrastructure.connectors.flight import FlightConnector


class FlightService:
    def __init__(self, flight_connector: FlightConnector):
        self._flight_connector = flight_connector

    def get_all(self, page: int, size: int) -> AllFlightsResponse:
        flights = self._flight_connector.get_flights(page, size)
        return flights
