import asyncio

import pytest

from app.services.exceptions import AirportNotFoundError
from app.presentation.api.schemas import AirportMeta, AirportResponse


class TestAirportService:
    def test_get_by_id_success(self, airport_service, mock_airport_repository, sample_airport):
        airport_id = 1
        mock_airport_repository.get_by_id.return_value = sample_airport

        result = asyncio.run(airport_service.get_by_id(airport_id))

        mock_airport_repository.get_by_id.assert_awaited_once_with(airport_id)
        assert isinstance(result, AirportResponse)
        assert result.id == sample_airport.id
        assert result.name == sample_airport.name
        assert result.city == sample_airport.city
        assert result.country == sample_airport.country

    def test_get_by_id_not_found(self, airport_service, mock_airport_repository):
        airport_id = 999
        mock_airport_repository.get_by_id.return_value = None

        with pytest.raises(AirportNotFoundError) as exc_info:
            asyncio.run(airport_service.get_by_id(airport_id))

        assert exc_info.value.id == airport_id
        mock_airport_repository.get_by_id.assert_awaited_once_with(airport_id)

    def test_get_all_success(
        self,
        airport_service,
        mock_airport_repository,
        sample_airport,
        sample_airport_2,
    ):
        mock_airport_repository.get_all.return_value = [
            sample_airport,
            sample_airport_2,
        ]

        result = asyncio.run(airport_service.get_all())

        mock_airport_repository.get_all.assert_awaited_once()
        assert isinstance(result, list)
        assert len(result) == 2
        assert all(isinstance(airport, AirportResponse) for airport in result)
        assert result[0].id == sample_airport.id
        assert result[1].id == sample_airport_2.id

    def test_get_all_empty(self, airport_service, mock_airport_repository):
        mock_airport_repository.get_all.return_value = []

        result = asyncio.run(airport_service.get_all())

        mock_airport_repository.get_all.assert_awaited_once()
        assert isinstance(result, list)
        assert len(result) == 0

    def test_save_new_airport_success(self, airport_service, mock_airport_repository):
        airport_meta = AirportMeta(name="Домодедово", city="Москва", country="Россия")
        expected_id = 3
        mock_airport_repository.save_new_airport.return_value = expected_id

        result = asyncio.run(airport_service.save_new_airport(airport_meta))

        mock_airport_repository.save_new_airport.assert_awaited_once()
        assert result == expected_id

    def test_update_airport_success(self, airport_service, mock_airport_repository, sample_airport):
        airport_id = 1
        airport_meta = AirportMeta(name="Шереметьево", city="Москва", country="Россия")
        mock_airport_repository.get_by_id.return_value = sample_airport

        asyncio.run(airport_service.update_airport(airport_id, airport_meta))

        mock_airport_repository.get_by_id.assert_awaited_once_with(airport_id)
        mock_airport_repository.update_airport.assert_awaited_once_with(airport_id, airport_meta)

    def test_update_airport_not_found(self, airport_service, mock_airport_repository):
        airport_id = 999
        airport_meta = AirportMeta(name="Шереметьево", city="Москва", country="Россия")
        mock_airport_repository.get_by_id.return_value = None

        with pytest.raises(AirportNotFoundError) as exc_info:
            asyncio.run(airport_service.update_airport(airport_id, airport_meta))

        assert exc_info.value.id == airport_id
        mock_airport_repository.get_by_id.assert_awaited_once_with(airport_id)
        mock_airport_repository.update_airport.assert_not_awaited()

    def test_delete_airport_success(self, airport_service, mock_airport_repository, sample_airport):
        airport_id = 1
        mock_airport_repository.get_by_id.return_value = sample_airport

        asyncio.run(airport_service.delete_airport(airport_id))

        mock_airport_repository.get_by_id.assert_awaited_once_with(airport_id)
        mock_airport_repository.delete_airport.assert_awaited_once_with(airport_id)

    def test_delete_airport_not_found(self, airport_service, mock_airport_repository):
        airport_id = 999
        mock_airport_repository.get_by_id.return_value = None

        with pytest.raises(AirportNotFoundError) as exc_info:
            asyncio.run(airport_service.delete_airport(airport_id))

        assert exc_info.value.id == airport_id
        mock_airport_repository.get_by_id.assert_awaited_once_with(airport_id)
        mock_airport_repository.delete_airport.assert_not_awaited()
