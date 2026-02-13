import asyncio

import pytest

from app.services.exceptions import FlightNotFoundError
from app.presentation.api.schemas import FlightMeta, FlightResponse


class TestFlightService:
    def test_get_by_id_success(self, flight_service, mock_flight_repository, sample_flight):
        flight_id = 1
        mock_flight_repository.get_by_id.return_value = sample_flight

        result = asyncio.run(flight_service.get_by_id(flight_id))

        mock_flight_repository.get_by_id.assert_awaited_once_with(flight_id)
        assert isinstance(result, FlightResponse)
        assert result.id == sample_flight.id
        assert result.flight_number == sample_flight.flight_number
        assert result.from_airport_id == sample_flight.from_airport_id
        assert result.to_airport_id == sample_flight.to_airport_id
        assert result.price == sample_flight.price

    def test_get_by_id_not_found(self, flight_service, mock_flight_repository):
        flight_id = 999
        mock_flight_repository.get_by_id.return_value = None

        with pytest.raises(FlightNotFoundError) as exc_info:
            asyncio.run(flight_service.get_by_id(flight_id))

        assert exc_info.value.id == flight_id
        mock_flight_repository.get_by_id.assert_awaited_once_with(flight_id)

    def test_get_all_success(self, flight_service, mock_flight_repository, sample_flight):
        mock_flight_repository.get_all.return_value = ([sample_flight], 1)

        result, total = asyncio.run(flight_service.get_all(page=1, size=10))

        mock_flight_repository.get_all.assert_awaited_once_with(1, 10)
        assert isinstance(result, list)
        assert len(result) == 1
        assert all(isinstance(flight, FlightResponse) for flight in result)
        assert result[0].id == sample_flight.id
        assert total == 1

    def test_get_all_empty(self, flight_service, mock_flight_repository):
        mock_flight_repository.get_all.return_value = ([], 0)

        result, total = asyncio.run(flight_service.get_all(page=1, size=10))

        mock_flight_repository.get_all.assert_awaited_once_with(1, 10)
        assert isinstance(result, list)
        assert len(result) == 0
        assert total == 0

    def test_get_all_with_pagination(self, flight_service, mock_flight_repository, sample_flight):
        mock_flight_repository.get_all.return_value = ([sample_flight], 10)

        result, total = asyncio.run(flight_service.get_all(page=2, size=5))

        mock_flight_repository.get_all.assert_awaited_once_with(2, 5)
        assert isinstance(result, list)
        assert len(result) == 1
        assert total == 10

    def test_save_new_flight_success(self, flight_service, mock_flight_repository):
        flight_meta = FlightMeta(flight_number="AFL032", from_airport_id=1, to_airport_id=2, price=2000)
        expected_id = 2
        mock_flight_repository.save_new_flight.return_value = expected_id

        result = asyncio.run(flight_service.save_new_flight(flight_meta))

        mock_flight_repository.save_new_flight.assert_awaited_once()
        assert result == expected_id

    def test_update_flight_success(self, flight_service, mock_flight_repository, sample_flight):
        flight_id = 1
        flight_meta = FlightMeta(flight_number="AFL031", from_airport_id=2, to_airport_id=1, price=1600)
        mock_flight_repository.get_by_id.return_value = sample_flight

        asyncio.run(flight_service.update_flight(flight_id, flight_meta))

        mock_flight_repository.get_by_id.assert_awaited_once_with(flight_id)
        mock_flight_repository.update_flight.assert_awaited_once_with(flight_id, flight_meta)

    def test_update_flight_not_found(self, flight_service, mock_flight_repository):
        flight_id = 999
        flight_meta = FlightMeta(flight_number="AFL031", from_airport_id=2, to_airport_id=1, price=1600)
        mock_flight_repository.get_by_id.return_value = None

        with pytest.raises(FlightNotFoundError) as exc_info:
            asyncio.run(flight_service.update_flight(flight_id, flight_meta))

        assert exc_info.value.id == flight_id
        mock_flight_repository.get_by_id.assert_awaited_once_with(flight_id)
        mock_flight_repository.update_flight.assert_not_awaited()

    def test_delete_flight_success(self, flight_service, mock_flight_repository, sample_flight):
        flight_id = 1
        mock_flight_repository.get_by_id.return_value = sample_flight

        asyncio.run(flight_service.delete_flight(flight_id))

        mock_flight_repository.get_by_id.assert_awaited_once_with(flight_id)
        mock_flight_repository.delete_flight.assert_awaited_once_with(flight_id)

    def test_delete_flight_not_found(self, flight_service, mock_flight_repository):
        flight_id = 999
        mock_flight_repository.get_by_id.return_value = None

        with pytest.raises(FlightNotFoundError) as exc_info:
            asyncio.run(flight_service.delete_flight(flight_id))

        assert exc_info.value.id == flight_id
        mock_flight_repository.get_by_id.assert_awaited_once_with(flight_id)
        mock_flight_repository.delete_flight.assert_not_awaited()
