from datetime import datetime

from pydantic import BaseModel, ConfigDict, constr


class AirportMeta(BaseModel):
    name: constr(min_length=1, max_length=255)  # type: ignore
    city: constr(min_length=1, max_length=255)  # type: ignore
    country: constr(min_length=1, max_length=255)  # type: ignore


class AirportResponse(AirportMeta):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: constr(min_length=1, max_length=255)  # type: ignore
    city: constr(min_length=1, max_length=255)  # type: ignore
    country: constr(min_length=1, max_length=255)  # type: ignore


class AllAirportsResponse(BaseModel):
    airports: list[AirportResponse]


class FlightMeta(BaseModel):
    flight_number: constr(min_length=1, max_length=20)  # type: ignore
    from_airport_id: int
    to_airport_id: int
    price: int


class FlightResponse(BaseModel):
    flightNumber: str
    fromAirport: str
    toAirport: str
    date: str
    price: int


class PaginationInfo(BaseModel):
    page: int
    pageSize: int
    totalElements: int


class PaginationResponse(BaseModel):
    page: int
    pageSize: int
    totalElements: int
    items: list[FlightResponse]


class AllFlightsResponse(PaginationResponse):
    pass


class HistoryItem(BaseModel):
    date: datetime
    ticketUid: str
    balanceDiff: int
    operationType: str

    model_config = ConfigDict(from_attributes=True)


class MeResponse(BaseModel):
    balance: int
    status: str
    history: list[HistoryItem]


class SetBalanceRequest(BaseModel):
    balance: int


class CreateHistoryRequest(BaseModel):
    ticketUid: str
    balanceDiff: int
    operationType: str


class TicketCreateRequest(BaseModel):
    flightNumber: str
    price: int
    paidFromBalance: bool


class TicketResponse(BaseModel):
    ticketUid: str
    flightNumber: str
    fromAirport: str
    toAirport: str
    date: str
    price: int
    status: str


class PrivilegeShortInfo(BaseModel):
    balance: int
    status: str


class TicketPurchaseResponse(BaseModel):
    ticketUid: str
    flightNumber: str
    fromAirport: str
    toAirport: str
    date: str
    price: int
    paidByMoney: int
    paidByBonuses: int
    status: str
    privilege: PrivilegeShortInfo


class UserInfoResponse(BaseModel):
    tickets: list[TicketResponse]
    privilege: PrivilegeShortInfo


class PrivilegeInfoResponse(BaseModel):
    balance: int
    status: str
    history: list[HistoryItem]


class ErrorResponse(BaseModel):
    message: str
