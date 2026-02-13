from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, ConfigDict, constr

from app.services.enums import TicketStatus


class TicketCreateRequest(BaseModel):
    flightNumber: constr(min_length=1, max_length=20)  # type: ignore
    price: int
    paidFromBalance: bool


class TicketPurchaseResponse(BaseModel):
    ticketUid: UUID
    flightNumber: constr(min_length=1, max_length=20)  # type: ignore
    price: int
    paidByMoney: int
    paidByBonuses: int
    status: TicketStatus
    date: datetime


class TicketMeta(BaseModel):
    username: constr(min_length=1, max_length=80)  # type: ignore
    flight_number: constr(min_length=1, max_length=20)  # type: ignore
    price: int
    status: TicketStatus


class TicketResponse(TicketMeta):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ticket_uid: UUID


class AllTicketsResponse(BaseModel):
    page: int
    pageSize: int
    totalElements: int
    items: list[TicketResponse]


class FlightMeta(BaseModel):
    flight_number: constr(min_length=1, max_length=20)  # type: ignore
    from_airport_id: int
    to_airport_id: int
    price: int


class FlightResponse(FlightMeta):
    model_config = ConfigDict(from_attributes=True)

    id: int
    datetime: datetime


class GatewayFlightResponse(BaseModel):
    flightNumber: str
    fromAirport: str
    toAirport: str
    date: str
    price: int


class GatewayAllFlightsResponse(BaseModel):
    page: int
    pageSize: int
    totalElements: int
    items: list[GatewayFlightResponse]


class AllFlightsResponse(BaseModel):
    page: int
    pageSize: int
    totalElements: int
    items: list[FlightResponse]
