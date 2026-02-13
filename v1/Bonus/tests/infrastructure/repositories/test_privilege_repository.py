import uuid
import asyncio

from datetime import datetime
from unittest.mock import MagicMock

from app.db.models.privilege_history import PrivilegeHistoryDB


class TestPrivilegeRepository:
    def test_create_new_user(self, privilege_repository, mock_db_session):
        username = "testuser"

        def set_id(*args, **kwargs):
            if hasattr(mock_db_session, "_added_obj"):
                mock_db_session._added_obj.id = 1

        async def mock_flush(*args, **kwargs):
            set_id()

        mock_db_session.flush.side_effect = mock_flush
        mock_db_session.add.side_effect = lambda obj: setattr(mock_db_session, "_added_obj", obj)

        result = asyncio.run(privilege_repository.create_new_user(username))

        mock_db_session.add.assert_called_once()
        mock_db_session.flush.assert_awaited_once()
        mock_db_session.commit.assert_awaited_once()
        assert isinstance(result, int)
        assert result == 1

    def test_get_user_found(self, privilege_repository, mock_db_session, sample_user):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_user
        mock_db_session.execute.return_value = mock_result

        result = asyncio.run(privilege_repository.get_user("testuser"))

        mock_db_session.execute.assert_awaited_once()
        assert result == sample_user
        assert result.username == "testuser"

    def test_get_user_not_found(self, privilege_repository, mock_db_session):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result

        result = asyncio.run(privilege_repository.get_user("nonexistent"))

        mock_db_session.execute.assert_awaited_once()
        assert result is None

    def test_delete_user(self, privilege_repository, mock_db_session):
        username = "testuser"

        asyncio.run(privilege_repository.delete_user(username))

        mock_db_session.execute.assert_awaited_once()
        mock_db_session.commit.assert_awaited_once()

    def test_set_balance(self, privilege_repository, mock_db_session, sample_user):
        username = "testuser"
        new_balance = 500
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_user
        mock_db_session.execute.return_value = mock_result

        asyncio.run(privilege_repository.set_balance(username, new_balance))

        assert sample_user.balance == new_balance
        mock_db_session.commit.assert_awaited_once()
        mock_db_session.refresh.assert_awaited_once_with(sample_user)

    def test_create_history_record(self, privilege_repository, mock_db_session, sample_user):
        username = "testuser"
        ticket_uid = uuid.uuid4()
        balance_diff = 150
        operation_type = "FILL_IN_BALANCE"

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_user
        mock_db_session.execute.return_value = mock_result

        asyncio.run(privilege_repository.create_history_record(username, ticket_uid, balance_diff, operation_type))

        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_awaited_once()
        added_obj = mock_db_session.add.call_args[0][0]
        assert isinstance(added_obj, PrivilegeHistoryDB)
        assert added_obj.privilege_id == sample_user.id
        assert added_obj.ticket_uid == ticket_uid
        assert added_obj.balance_diff == balance_diff
        assert added_obj.operation_type == operation_type

    def test_get_user_history(self, privilege_repository, mock_db_session, sample_user):
        username = "testuser"
        history_record = PrivilegeHistoryDB(
            privilege_id=sample_user.id,
            ticket_uid=uuid.uuid4(),
            datetime=datetime.now(),
            balance_diff=150,
            operation_type="FILL_IN_BALANCE",
        )

        mock_result_user = MagicMock()
        mock_result_user.scalar_one_or_none.return_value = sample_user

        mock_result_history = MagicMock()
        mock_result_history.scalars.return_value.all.return_value = [history_record]

        mock_db_session.execute.side_effect = [mock_result_user, mock_result_history]

        result = asyncio.run(privilege_repository.get_user_history(username))

        assert len(result) == 1
        assert result[0] == history_record
