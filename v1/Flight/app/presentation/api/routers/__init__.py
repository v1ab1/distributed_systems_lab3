from enum import Enum
from typing import Any, TypedDict

from fastapi import FastAPI, APIRouter

from app.presentation.api.routers.manage import router as manage_router
from app.presentation.api.routers.v1.flight import router as flight_router
from app.presentation.api.routers.v1.airport import router as airport_router


class RouterConfig(TypedDict):
    """Конфигурация роутера для регистрации в приложении."""

    router: APIRouter
    tags: list[str | Enum]
    dependencies: list[Any] | None


MIDDLEWARES = []  # type: ignore

routers: list[RouterConfig] = [
    {
        "router": manage_router,
        "tags": ["Manage"],
        "dependencies": MIDDLEWARES,
    },
    {"router": flight_router, "tags": ["Flight"], "dependencies": MIDDLEWARES},
    {"router": airport_router, "tags": ["Airport"], "dependencies": MIDDLEWARES},
]


def add_routers(app: FastAPI) -> None:
    for router_config in routers:
        app.include_router(
            router_config["router"], tags=router_config["tags"], dependencies=router_config["dependencies"]
        )
