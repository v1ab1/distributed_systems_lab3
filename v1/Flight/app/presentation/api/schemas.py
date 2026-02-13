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


class FlightResponse(FlightMeta):
    model_config = ConfigDict(from_attributes=True)

    id: int
    datetime: datetime


class PaginationInfo(BaseModel):
    page: int
    pageSize: int
    totalElements: int


class AllFlightsResponse(BaseModel):
    page: int
    pageSize: int
    totalElements: int
    items: list[FlightResponse]
