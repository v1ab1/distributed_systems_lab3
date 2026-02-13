import uuid
import asyncio

from unittest.mock import MagicMock

from app.services.enums import TicketStatus


class TestTicketRepository:
    def test_get_all(self, ticket_repository, mock_db_session, sample_ticket):
        mock_count_result = MagicMock()
        mock_count_result.scalar.return_value = 1

        mock_tickets_result = MagicMock()
        mock_tickets_result.scalars.return_value.all.return_value = [sample_ticket]

        mock_db_session.execute.side_effect = [
            mock_count_result,
            mock_tickets_result,
        ]

        tickets, total = asyncio.run(ticket_repository.get_all(page=1, size=10))

        assert len(tickets) == 1
        assert total == 1
        assert tickets[0] == sample_ticket

    def test_get_by_ticket_uid_found(self, ticket_repository, mock_db_session, sample_ticket):
        ticket_uid = str(sample_ticket.ticket_uid)
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_ticket
        mock_db_session.execute.return_value = mock_result

        result = asyncio.run(ticket_repository.get_by_ticket_uid(ticket_uid))

        assert result == sample_ticket
        assert result.username == "testuser"

    def test_get_by_ticket_uid_not_found(self, ticket_repository, mock_db_session):
        ticket_uid = str(uuid.uuid4())
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result

        result = asyncio.run(ticket_repository.get_by_ticket_uid(ticket_uid))

        assert result is None

    def test_get_by_username(self, ticket_repository, mock_db_session, sample_ticket):
        username = "testuser"
        mock_count_result = MagicMock()
        mock_count_result.scalar.return_value = 1

        mock_tickets_result = MagicMock()
        mock_tickets_result.scalars.return_value.all.return_value = [sample_ticket]

        mock_db_session.execute.side_effect = [
            mock_count_result,
            mock_tickets_result,
        ]

        tickets, total = asyncio.run(ticket_repository.get_by_username(username, page=1, size=10))

        assert len(tickets) == 1
        assert total == 1
        assert tickets[0] == sample_ticket

    def test_save_new_ticket(self, ticket_repository, mock_db_session):
        from app.db.models.ticket import TicketDB

        ticket_uid = uuid.uuid4()
        ticket = TicketDB(
            username="testuser",
            flight_number="AFL031",
            price=1500,
            status=TicketStatus.PAID.value,
            ticket_uid=ticket_uid,
        )

        async def mock_flush(*args, **kwargs):
            ticket.id = 1

        mock_db_session.flush.side_effect = mock_flush

        result = asyncio.run(ticket_repository.save_new_ticket(ticket))

        mock_db_session.add.assert_called_once_with(ticket)
        mock_db_session.flush.assert_awaited_once()
        mock_db_session.commit.assert_awaited_once()
        assert result == str(ticket_uid)

    def test_cancel_ticket(self, ticket_repository, mock_db_session, sample_ticket):
        ticket_uid = str(sample_ticket.ticket_uid)
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_ticket
        mock_db_session.execute.return_value = mock_result

        asyncio.run(ticket_repository.cancel_ticket(ticket_uid))

        assert sample_ticket.status == "CANCELED"
        mock_db_session.commit.assert_awaited_once()
        mock_db_session.refresh.assert_awaited_once_with(sample_ticket)
