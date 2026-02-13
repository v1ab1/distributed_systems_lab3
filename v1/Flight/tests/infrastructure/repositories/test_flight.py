import asyncio

from unittest.mock import MagicMock


class TestFlightRepository:
    def test_save_new_flight(self, flight_repository, mock_db_session):
        from datetime import datetime

        from app.db.models.flight import FlightDB

        flight = FlightDB(
            flight_number="AFL031",
            datetime=datetime(2021, 10, 8, 20, 0),
            from_airport_id=2,
            to_airport_id=1,
            price=1500,
        )

        def set_id(*args, **kwargs):
            if hasattr(mock_db_session, "_added_obj"):
                mock_db_session._added_obj.id = 1

        async def mock_flush(*args, **kwargs):
            set_id()

        mock_db_session.flush.side_effect = mock_flush
        mock_db_session.add.side_effect = lambda obj: setattr(mock_db_session, "_added_obj", obj)

        result = asyncio.run(flight_repository.save_new_flight(flight))

        mock_db_session.add.assert_called_once()
        mock_db_session.flush.assert_awaited_once()
        mock_db_session.commit.assert_awaited_once()
        assert isinstance(result, int)
        assert result == 1

    def test_get_by_id_found(self, flight_repository, mock_db_session, sample_flight):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_flight
        mock_db_session.execute.return_value = mock_result

        result = asyncio.run(flight_repository.get_by_id(1))

        mock_db_session.execute.assert_awaited_once()
        assert result == sample_flight
        assert result.flight_number == "AFL031"

    def test_get_by_id_not_found(self, flight_repository, mock_db_session):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result

        result = asyncio.run(flight_repository.get_by_id(999))

        mock_db_session.execute.assert_awaited_once()
        assert result is None

    def test_get_all(self, flight_repository, mock_db_session, sample_flight):
        mock_count_result = MagicMock()
        mock_count_result.scalar.return_value = 1

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_flight]

        mock_db_session.execute.side_effect = [
            mock_count_result,
            mock_result,
        ]

        result, total = asyncio.run(flight_repository.get_all(page=1, size=10))

        assert mock_db_session.execute.await_count == 2
        assert len(result) == 1
        assert result[0] == sample_flight
        assert total == 1

    def test_get_all_with_pagination(self, flight_repository, mock_db_session, sample_flight):
        mock_count_result = MagicMock()
        mock_count_result.scalar.return_value = 10

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_flight]

        mock_db_session.execute.side_effect = [
            mock_count_result,
            mock_result,
        ]

        result, total = asyncio.run(flight_repository.get_all(page=2, size=5))

        assert mock_db_session.execute.await_count == 2
        assert len(result) == 1
        assert total == 10

    def test_delete_flight(self, flight_repository, mock_db_session):
        flight_id = 1
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = MagicMock()
        mock_db_session.execute.return_value = mock_result

        asyncio.run(flight_repository.delete_flight(flight_id))

        assert mock_db_session.execute.await_count == 2
        mock_db_session.commit.assert_awaited_once()

    def test_update_flight(self, flight_repository, mock_db_session, sample_flight):
        from app.presentation.api.schemas import FlightMeta

        flight_id = 1
        flight_meta = FlightMeta(
            flight_number="AFL031",
            from_airport_id=2,
            to_airport_id=1,
            price=1600,
        )
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_flight
        mock_db_session.execute.return_value = mock_result

        asyncio.run(flight_repository.update_flight(flight_id, flight_meta))

        assert sample_flight.price == 1600
        mock_db_session.commit.assert_awaited_once()
        mock_db_session.refresh.assert_awaited_once_with(sample_flight)
