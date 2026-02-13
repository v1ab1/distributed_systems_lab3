from enum import Enum
from typing import Any, TypedDict

from fastapi import FastAPI, APIRouter

from app.presentation.api.routers.v1.me import router as me_router
from app.presentation.api.routers.manage import router as manage_router
from app.presentation.api.routers.v1.balance import router as balance_router
from app.presentation.api.routers.v1.flights import router as flights_router
from app.presentation.api.routers.v1.tickets import router as tickets_router
from app.presentation.api.routers.v1.privilege import router as privilege_router


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
    {"router": flights_router, "tags": ["Gateway API"], "dependencies": MIDDLEWARES},
    {"router": me_router, "tags": ["Gateway API"], "dependencies": MIDDLEWARES},
    {"router": balance_router, "tags": ["Balance"], "dependencies": MIDDLEWARES},
    {"router": tickets_router, "tags": ["Gateway API"], "dependencies": MIDDLEWARES},
    {"router": privilege_router, "tags": ["Gateway API"], "dependencies": MIDDLEWARES},
]


def add_routers(app: FastAPI) -> None:
    for router_config in routers:
        app.include_router(
            router_config["router"], tags=router_config["tags"], dependencies=router_config["dependencies"]
        )
