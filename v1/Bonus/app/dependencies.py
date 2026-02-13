from app.services import PrivilegeService
from app.db.engine import get_db
from app.infrastructure.repositories import PrivilegeRepository


async def get_privilege_service() -> PrivilegeService:  # type: ignore
    async for session in get_db():
        persons_repository = PrivilegeRepository(session)

        return PrivilegeService(persons_repository)
