import traceback

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.logger import persons_logger
from app.services.exceptions import UserNotFoundError, UsernameAlreadyExistError


async def person_not_found_error_handler(_: Request, exc: UserNotFoundError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"message": exc.message})


async def person_already_exist_error_handler(_: Request, exc: UsernameAlreadyExistError) -> JSONResponse:
    return JSONResponse(status_code=400, content={"message": exc.message})


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


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    persons_logger.error(f"Unhandled exception: {exc}", exc_info=True, extra={"traceback": traceback.format_exc()})
    return JSONResponse(
        status_code=500,
        content={"message": "Internal server error", "error": str(exc)},
    )


def add_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(UserNotFoundError, person_not_found_error_handler)  # type: ignore
    app.add_exception_handler(UsernameAlreadyExistError, person_already_exist_error_handler)  # type: ignore
    app.add_exception_handler(RequestValidationError, validation_error_handler)  # type: ignore
    app.add_exception_handler(Exception, general_exception_handler)
