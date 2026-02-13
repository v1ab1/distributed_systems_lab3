import uuid

from unittest.mock import AsyncMock, MagicMock

import pytest

from app.services.enums import TicketStatus
from app.db.models.ticket import TicketDB
from app.infrastructure.repositories.ticket import TicketRepository


@pytest.fixture
def mock_db_session():
    session = AsyncMock()
    session.add = MagicMock()
    session.flush = AsyncMock()
    session.commit = AsyncMock()
    session.execute = AsyncMock()
    session.refresh = AsyncMock()
    session.close = AsyncMock()
    return session


@pytest.fixture
def ticket_repository(mock_db_session):
    return TicketRepository(mock_db_session)


@pytest.fixture
def mock_ticket_repository():
    repository = AsyncMock(spec=TicketRepository)
    return repository


@pytest.fixture
def mock_gateway_connector():
    connector = AsyncMock()
    return connector


@pytest.fixture
def mock_bonus_connector():
    connector = AsyncMock()
    return connector


@pytest.fixture
def ticket_service(mock_ticket_repository, mock_gateway_connector, mock_bonus_connector):
    from app.services.ticket import TicketService

    return TicketService(mock_ticket_repository, mock_gateway_connector, mock_bonus_connector)


@pytest.fixture
def sample_ticket():
    ticket = TicketDB(
        username="testuser",
        flight_number="AFL031",
        price=1500,
        status=TicketStatus.PAID.value,
        ticket_uid=uuid.uuid4(),
    )
    ticket.id = 1
    return ticket


@pytest.fixture
def sample_flight():
    from app.presentation.api.schemas import GatewayFlightResponse

    return GatewayFlightResponse(
        flightNumber="AFL031",
        fromAirport="Санкт-Петербург Пулково",
        toAirport="Москва Шереметьево",
        date="2021-10-08 20:00",
        price=1500,
    )
