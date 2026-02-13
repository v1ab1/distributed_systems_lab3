from sqlalchemy import (
    UUID,
    TIMESTAMP,
    Column,
    String,
    Integer,
    ForeignKey,
    CheckConstraint,
)
from sqlalchemy.orm import relationship

from app.db.base import Base


class PrivilegeHistoryDB(Base):
    __tablename__ = "privilege_history"
    id = Column(Integer, primary_key=True)
    privilege_id = Column(Integer, ForeignKey("privilege.id"))
    ticket_uid = Column(UUID(as_uuid=True), nullable=False)
    datetime = Column(TIMESTAMP, nullable=False)
    balance_diff = Column(Integer, nullable=False)
    operation_type = Column(String(20), nullable=False)

    privilege = relationship("PrivilegeDB", backref="history")

    __table_args__ = (
        CheckConstraint("operation_type IN ('FILL_IN_BALANCE', 'DEBIT_THE_ACCOUNT')", name="check_operation_type"),
    )
