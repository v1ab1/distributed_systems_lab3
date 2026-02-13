from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.presentation.api import routers, handlers

load_dotenv(override=True)

app = FastAPI(
    title="Persons services",
    description=("Сервис, который предоставляет CRUD операции над пользователями"),
    version="1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_prefix="/api",
)

routers.add_routers(app)
handlers.add_exception_handlers(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
