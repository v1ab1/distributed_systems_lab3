from unittest.mock import AsyncMock, MagicMock

import pytest

from app.services.privilege import PrivilegeService
from app.db.models.privilege import PrivilegeDB
from app.infrastructure.repositories.privilege import PrivilegeRepository


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
def privilege_repository(mock_db_session):
    return PrivilegeRepository(mock_db_session)


@pytest.fixture
def mock_privilege_repository():
    repository = AsyncMock(spec=PrivilegeRepository)
    return repository


@pytest.fixture
def privilege_service(mock_privilege_repository):
    return PrivilegeService(mock_privilege_repository)


@pytest.fixture
def sample_user():
    user = PrivilegeDB(username="testuser", status="BRONZE", balance=100)
    user.id = 1
    return user


@pytest.fixture
def sample_user_no_balance():
    user = PrivilegeDB(username="newuser", status="BRONZE", balance=None)
    user.id = 2
    return user
