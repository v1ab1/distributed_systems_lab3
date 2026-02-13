from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.services.exceptions import (
    FlightNotFoundError,
    TicketNotFoundError,
    InsufficientBalanceError,
)


async def ticket_not_found_error_handler(_: Request, exc: TicketNotFoundError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"message": exc.message})


async def flight_not_found_error_handler(_: Request, exc: FlightNotFoundError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"message": exc.message})


async def insufficient_balance_error_handler(_: Request, exc: InsufficientBalanceError) -> JSONResponse:
    return JSONResponse(status_code=402, content={"message": exc.message})


async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    errors = {}
    for err in exc.errors():
        loc = err.get("loc", [])
        if loc and loc[0] == "body" and len(loc) == 2:
            field = loc[1]
        elif loc:
            field = ".".join(str(x) for x in loc[1:])
        else:
            field = "non_field"
        errors[field] = err.get("msg")

    return JSONResponse(status_code=400, content={"message": "Неверный запрос", "errors": errors})


def add_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(TicketNotFoundError, ticket_not_found_error_handler)  # type: ignore
    app.add_exception_handler(FlightNotFoundError, flight_not_found_error_handler)  # type: ignore
    app.add_exception_handler(InsufficientBalanceError, insufficient_balance_error_handler)  # type: ignore
    app.add_exception_handler(RequestValidationError, validation_error_handler)  # type: ignore
