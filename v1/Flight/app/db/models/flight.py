from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import TIMESTAMP

from app.db.base import Base


class FlightDB(Base):
    __tablename__ = "flight"

    id = Column(Integer, primary_key=True)
    flight_number = Column(String(20), nullable=False)
    datetime = Column(TIMESTAMP(timezone=True), nullable=False)
    from_airport_id = Column(Integer, ForeignKey("airport.id"))
    to_airport_id = Column(Integer, ForeignKey("airport.id"))
    price = Column(Integer, nullable=False)

    from_airport = relationship("AirportDB", foreign_keys=[from_airport_id], back_populates="departures")
    to_airport = relationship("AirportDB", foreign_keys=[to_airport_id], back_populates="arrivals")
