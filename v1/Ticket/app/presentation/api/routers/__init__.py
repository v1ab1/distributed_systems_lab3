from enum import Enum
from typing import Any, TypedDict

from fastapi import FastAPI, APIRouter

from app.presentation.api.routers.manage import router as manage_router
from app.presentation.api.routers.v1.ticket import router as ticket_router


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
    {"router": ticket_router, "tags": ["Ticket"], "dependencies": MIDDLEWARES},
]


def add_routers(app: FastAPI) -> None:
    for router_config in routers:
        app.include_router(
            router_config["router"], tags=router_config["tags"], dependencies=router_config["dependencies"]
        )
