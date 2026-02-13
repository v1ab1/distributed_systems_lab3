from typing import TYPE_CHECKING

from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship

from app.db.base import Base

if TYPE_CHECKING:
    pass


class AirportDB(Base):
    __tablename__ = "airport"

    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    city = Column(String(255))
    country = Column(String(255))

    departures = relationship("FlightDB", foreign_keys="FlightDB.from_airport_id", back_populates="from_airport")
    arrivals = relationship("FlightDB", foreign_keys="FlightDB.to_airport_id", back_populates="to_airport")
