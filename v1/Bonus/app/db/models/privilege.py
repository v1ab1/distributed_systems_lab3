from sqlalchemy import (
    Column,
    String,
    Integer,
    CheckConstraint,
)

from app.db.base import Base


class PrivilegeDB(Base):
    __tablename__ = "privilege"
    id = Column(Integer, primary_key=True)
    username = Column(String(80), nullable=False, unique=True)
    status = Column(String(80), nullable=False, default="BRONZE")
    balance = Column(Integer, nullable=False, default=0)

    __table_args__ = (CheckConstraint("status IN ('BRONZE', 'SILVER', 'GOLD')", name="check_status"),)
