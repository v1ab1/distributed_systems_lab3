from unittest.mock import MagicMock

import pytest

from app.infrastructure.connectors.bonus import BonusConnector
from app.infrastructure.connectors.flight import FlightConnector
from app.infrastructure.connectors.ticket import TicketConnector
from app.services.bonus import BonusService
from app.services.flight import FlightService
from app.services.ticket import TicketService


@pytest.fixture
def mock_flight_connector():
    return MagicMock(spec=FlightConnector)


@pytest.fixture
def mock_ticket_connector():
    return MagicMock(spec=TicketConnector)


@pytest.fixture
def mock_bonus_connector():
    return MagicMock(spec=BonusConnector)


@pytest.fixture
def flight_service(mock_flight_connector):
    return FlightService(mock_flight_connector)


@pytest.fixture
def ticket_service(mock_ticket_connector):
    return TicketService(mock_ticket_connector)


@pytest.fixture
def bonus_service(mock_bonus_connector):
    return BonusService(mock_bonus_connector)
