from app.services.bonus import BonusService
from app.services.flight import FlightService
from app.services.ticket import TicketService
from app.infrastructure.connectors.bonus import BonusConnector
from app.infrastructure.connectors.flight import FlightConnector
from app.infrastructure.connectors.ticket import TicketConnector


def get_flight_service() -> FlightService:
    flight_connector = FlightConnector()
    return FlightService(flight_connector)


def get_bonus_service() -> BonusService:
    bonus_connector = BonusConnector()
    return BonusService(bonus_connector)


def get_ticket_service() -> TicketService:
    ticket_connector = TicketConnector()
    return TicketService(ticket_connector)
