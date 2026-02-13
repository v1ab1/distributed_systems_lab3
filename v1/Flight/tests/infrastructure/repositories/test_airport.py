import asyncio

from unittest.mock import MagicMock


class TestAirportRepository:
    def test_save_new_airport(self, airport_repository, mock_db_session):
        from app.db.models.airport import AirportDB

        airport = AirportDB(name="Шереметьево", city="Москва", country="Россия")

        def set_id(*args, **kwargs):
            if hasattr(mock_db_session, "_added_obj"):
                mock_db_session._added_obj.id = 1

        async def mock_flush(*args, **kwargs):
            set_id()

        mock_db_session.flush.side_effect = mock_flush
        mock_db_session.add.side_effect = lambda obj: setattr(mock_db_session, "_added_obj", obj)

        result = asyncio.run(airport_repository.save_new_airport(airport))

        mock_db_session.add.assert_called_once()
        mock_db_session.flush.assert_awaited_once()
        mock_db_session.commit.assert_awaited_once()
        assert isinstance(result, int)
        assert result == 1

    def test_get_by_id_found(self, airport_repository, mock_db_session, sample_airport):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_airport
        mock_db_session.execute.return_value = mock_result

        result = asyncio.run(airport_repository.get_by_id(1))

        mock_db_session.execute.assert_awaited_once()
        assert result == sample_airport
        assert result.name == "Шереметьево"

    def test_get_by_id_not_found(self, airport_repository, mock_db_session):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result

        result = asyncio.run(airport_repository.get_by_id(999))

        mock_db_session.execute.assert_awaited_once()
        assert result is None

    def test_get_all(
        self,
        airport_repository,
        mock_db_session,
        sample_airport,
        sample_airport_2,
    ):
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [
            sample_airport,
            sample_airport_2,
        ]
        mock_db_session.execute.return_value = mock_result

        result = asyncio.run(airport_repository.get_all())

        mock_db_session.execute.assert_awaited_once()
        assert len(result) == 2
        assert result[0] == sample_airport
        assert result[1] == sample_airport_2

    def test_delete_airport(self, airport_repository, mock_db_session):
        airport_id = 1
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = MagicMock()
        mock_db_session.execute.return_value = mock_result

        asyncio.run(airport_repository.delete_airport(airport_id))

        assert mock_db_session.execute.await_count == 2
        mock_db_session.commit.assert_awaited_once()

    def test_update_airport(self, airport_repository, mock_db_session, sample_airport):
        from app.presentation.api.schemas import AirportMeta

        airport_id = 1
        airport_meta = AirportMeta(name="Шереметьево-2", city="Москва", country="Россия")
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_airport
        mock_db_session.execute.return_value = mock_result

        asyncio.run(airport_repository.update_airport(airport_id, airport_meta))

        assert sample_airport.name == "Шереметьево-2"
        mock_db_session.commit.assert_awaited_once()
        mock_db_session.refresh.assert_awaited_once_with(sample_airport)
