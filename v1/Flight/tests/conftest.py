from unittest.mock import AsyncMock, MagicMock

import pytest

from app.services.flight import FlightService
from app.db.models.flight import FlightDB
from app.services.airport import AirportService
from app.db.models.airport import AirportDB
from app.infrastructure.repositories.flight import FlightRepository
from app.infrastructure.repositories.airport import AirportRepository


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
def airport_repository(mock_db_session):
    return AirportRepository(mock_db_session)


@pytest.fixture
def flight_repository(mock_db_session):
    return FlightRepository(mock_db_session)


@pytest.fixture
def mock_airport_repository():
    repository = AsyncMock(spec=AirportRepository)
    return repository


@pytest.fixture
def mock_flight_repository():
    repository = AsyncMock(spec=FlightRepository)
    return repository


@pytest.fixture
def airport_service(mock_airport_repository):
    return AirportService(mock_airport_repository)


@pytest.fixture
def flight_service(mock_flight_repository):
    return FlightService(mock_flight_repository)


@pytest.fixture
def sample_airport():
    airport = AirportDB(name="Шереметьево", city="Москва", country="Россия")
    airport.id = 1
    return airport


@pytest.fixture
def sample_airport_2():
    airport = AirportDB(name="Пулково", city="Санкт-Петербург", country="Россия")
    airport.id = 2
    return airport


@pytest.fixture
def sample_flight(sample_airport, sample_airport_2):
    from datetime import datetime

    flight = FlightDB(
        flight_number="AFL031",
        datetime=datetime(2021, 10, 8, 20, 0),
        from_airport_id=2,
        to_airport_id=1,
        price=1500,
    )
    flight.id = 1
    return flight
