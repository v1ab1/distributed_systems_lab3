import uuid

from sqlalchemy import Column, String, Integer, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base


class TicketDB(Base):
    __tablename__ = "ticket"
    __table_args__ = (CheckConstraint("status IN ('PAID', 'CANCELED')", name="check_status"),)

    id = Column(Integer, primary_key=True)
    ticket_uid = Column(UUID(as_uuid=True), unique=True, nullable=False, default=uuid.uuid4)
    username = Column(String(80), nullable=False)
    flight_number = Column(String(20), nullable=False)
    price = Column(Integer, nullable=False)
    status = Column(String(20), nullable=False)
