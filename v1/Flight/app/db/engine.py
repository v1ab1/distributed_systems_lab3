import os

from functools import lru_cache
from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.logger import persons_logger

load_dotenv(override=True)

DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")


def get_database_url() -> str:
    url = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    persons_logger.info(
        "Подключение к БД: postgresql+asyncpg://%s@%s:%s/%s",
        DB_USER,
        DB_HOST,
        DB_PORT,
        DB_NAME,
    )
    return url


@lru_cache(maxsize=1)
def get_engine() -> AsyncEngine:
    database_url = get_database_url()
    engine = create_async_engine(
        database_url,
        echo=True,
        pool_pre_ping=True,
        pool_size=1000,
        max_overflow=1000,
        connect_args={"timeout": 5},
    )
    return engine


@lru_cache(maxsize=1)
def get_sessionmaker(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        autoflush=False,
    )


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    engine = get_engine()
    sessionmaker = get_sessionmaker(engine)
    async with sessionmaker() as session:
        yield session
        await session.close()


@asynccontextmanager
async def lazy_db_session() -> AsyncGenerator[AsyncSession, None]:
    engine = get_engine()
    sessionmaker = get_sessionmaker(engine)
    async with sessionmaker() as session:
        yield session
        await session.close()


async def init_db() -> None:
    import app.db.models  # noqa: F401

    from app.db.base import Base

    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def seed_database() -> None:
    from datetime import datetime

    from sqlalchemy import select

    from app.db.models.flight import FlightDB
    from app.db.models.airport import AirportDB

    persons_logger.info("Проверка начальных данных в БД...")

    async with lazy_db_session() as session:
        result = await session.execute(select(AirportDB))
        existing_airports = result.scalars().all()

        if existing_airports:
            persons_logger.info("БД уже содержит данные. Пропуск заполнения.")
            return

        persons_logger.info("Заполнение БД начальными данными...")

        airport1 = AirportDB(id=1, name="Шереметьево", city="Москва", country="Россия")
        airport2 = AirportDB(id=2, name="Пулково", city="Санкт-Петербург", country="Россия")

        session.add(airport1)
        session.add(airport2)
        await session.flush()

        flight1 = FlightDB(
            id=1,
            flight_number="AFL031",
            datetime=datetime(2021, 10, 8, 20, 0),
            from_airport_id=2,
            to_airport_id=1,
            price=1500,
        )

        session.add(flight1)
        await session.commit()

        persons_logger.info("БД успешно заполнена начальными данными!")
