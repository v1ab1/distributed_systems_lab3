from app.presentation.api.schemas import MeResponse, PrivilegeInfoResponse, HistoryItem
from datetime import datetime


class TestBonusService:
    def test_get_me_success(self, bonus_service, mock_bonus_connector):
        username = "test_user"
        
        expected_response = MeResponse(
            balance=150,
            status="BRONZE",
            history=[
                HistoryItem(
                    date=datetime(2021, 10, 8, 19, 59, 19),
                    ticketUid="123e4567-e89b-12d3-a456-426614174000",
                    balanceDiff=150,
                    operationType="FILL_IN_BALANCE",
                )
            ],
        )
        
        mock_bonus_connector.get_me.return_value = expected_response
        
        result = bonus_service.get_me(username)
        
        mock_bonus_connector.get_me.assert_called_once_with(username)
        assert isinstance(result, MeResponse)
        assert result.balance == 150
        assert result.status == "BRONZE"
        assert len(result.history) == 1

    def test_get_privilege_info_success(self, bonus_service, mock_bonus_connector):
        username = "test_user"
        
        expected_me_response = MeResponse(
            balance=150,
            status="BRONZE",
            history=[
                HistoryItem(
                    date=datetime(2021, 10, 8, 19, 59, 19),
                    ticketUid="123e4567-e89b-12d3-a456-426614174000",
                    balanceDiff=150,
                    operationType="FILL_IN_BALANCE",
                )
            ],
        )
        
        mock_bonus_connector.get_me.return_value = expected_me_response
        
        result = bonus_service.get_privilege_info(username)
        
        mock_bonus_connector.get_me.assert_called_once_with(username)
        assert isinstance(result, PrivilegeInfoResponse)
        assert result.balance == 150
        assert result.status == "BRONZE"
        assert len(result.history) == 1

    def test_get_user_balance_success(self, bonus_service, mock_bonus_connector):
        username = "test_user"
        
        mock_bonus_connector.get_user_balance.return_value = 150
        
        result = bonus_service.get_user_balance(username)
        
        mock_bonus_connector.get_user_balance.assert_called_once_with(username)
        assert result == 150

    def test_change_user_balance_success(self, bonus_service, mock_bonus_connector):
        username = "test_user"
        balance_diff = 100
        
        mock_bonus_connector.change_user_balance.return_value = None
        
        result = bonus_service.change_user_balance(username, balance_diff)
        
        mock_bonus_connector.change_user_balance.assert_called_once_with(username, balance_diff)
        assert result is None

    def test_create_history_record_success(self, bonus_service, mock_bonus_connector):
        username = "test_user"
        ticket_uid = "123e4567-e89b-12d3-a456-426614174000"
        balance_diff = 150
        operation_type = "FILL_IN_BALANCE"
        
        mock_bonus_connector.create_history_record.return_value = None
        
        result = bonus_service.create_history_record(username, ticket_uid, balance_diff, operation_type)
        
        mock_bonus_connector.create_history_record.assert_called_once_with(
            username, ticket_uid, balance_diff, operation_type
        )
        assert result is None
