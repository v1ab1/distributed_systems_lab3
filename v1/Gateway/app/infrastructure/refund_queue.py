"""Очередь возвратов бонусов при отмене билета: при недоступности Bonus ставим в очередь и обрабатываем позже."""

import os
import json
import time

from collections.abc import Callable

import redis

from dotenv import load_dotenv

load_dotenv(override=True)

QUEUE_KEY = "gateway:ticket_refund_queue"
POLL_INTERVAL = 5
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")


def _get_redis() -> redis.Redis:
    return redis.from_url(REDIS_URL, decode_responses=True)


def enqueue_refund(ticket_uid: str, username: str) -> None:
    """Поставить в очередь задачу возврата бонусов (повторный вызов cancel в Ticket service)."""
    try:
        r = _get_redis()
        payload = json.dumps({"ticket_uid": ticket_uid, "username": username})
        r.lpush(QUEUE_KEY, payload)
    except redis.RedisError:  # noqa: S110
        pass


def process_one(cancel_fn: Callable[[str, str], None]) -> bool:
    """Обработать один элемент очереди. Возвращает True если обработан хотя бы один."""
    try:
        r = _get_redis()
        raw = r.rpop(QUEUE_KEY)
        if not raw or not isinstance(raw, str):
            return False
        data = json.loads(raw)
        ticket_uid = data.get("ticket_uid")
        username = data.get("username")
        if not ticket_uid or not username:
            return True
        try:
            cancel_fn(ticket_uid, username)
        except Exception:
            r.lpush(QUEUE_KEY, raw)
        return True
    except (redis.RedisError, json.JSONDecodeError):
        return False


def _default_cancel(ticket_uid: str, username: str) -> None:
    from app.infrastructure.connectors.ticket import TicketConnector

    TicketConnector().cancel_ticket(ticket_uid, username)


def run_worker(
    cancel_fn: Callable[[str, str], None] | None = None,
    poll_interval: float = POLL_INTERVAL,
) -> None:
    """Фоновый цикл: раз в poll_interval секунд обрабатывать очередь."""
    fn = cancel_fn or _default_cancel
    while True:
        try:
            while process_one(fn):
                pass
        except Exception:  # noqa: S110
            pass
        time.sleep(poll_interval)
