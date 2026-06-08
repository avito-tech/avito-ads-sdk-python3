"""Общие фикстуры и помощники тестов (sync + async).

HTTP мокируется встроенным ``httpx.MockTransport`` — он одинаково работает и для
``httpx.Client``, и для ``httpx.AsyncClient``, поэтому один и тот же набор тестов
проверяет оба режима. Реальная сеть не используется.
"""

from __future__ import annotations

import inspect
import json
from typing import Any, Dict, List, Optional, Tuple

import httpx
import pytest

from avito_ads import AsyncClient, Client, Configuration

TOKEN_PATH = "/token"
PRODUCTION = "https://api.avito.ru/ads"
SANDBOX = "https://api.avito.ru/ads-sandbox"
ACCOUNT_ID = 123456789
ACCT_PATH = f"/ads/v1/account/{ACCOUNT_ID}"


class MockRouter:
    """Записывает запросы и отдаёт заранее заданные ответы по ключу (метод, путь).

    Если для маршрута добавлено несколько ответов, они выдаются по очереди;
    последний ответ остаётся «залипшим» (используется для повторных попыток).
    """

    def __init__(self) -> None:
        self.requests: List[httpx.Request] = []
        self._queues: Dict[Tuple[str, str], List[Dict[str, Any]]] = {}

    def add(
        self,
        method: str,
        path: str,
        *,
        json: Optional[Any] = None,
        text: Optional[str] = None,
        status: int = 200,
        headers: Optional[Dict[str, str]] = None,
    ) -> "MockRouter":
        key = (method.upper(), path)
        self._queues.setdefault(key, []).append(
            {"status": status, "json": json, "text": text, "headers": headers or {}}
        )
        return self

    def add_token(
        self, token: str = "test-token", expires_in: int = 86400, status: int = 200
    ) -> "MockRouter":
        body = {"access_token": token, "expires_in": expires_in, "token_type": "Bearer"}
        if status != 200:
            return self.add("POST", TOKEN_PATH, text="nope", status=status)
        return self.add("POST", TOKEN_PATH, json=body, status=status)

    @staticmethod
    def _build(spec: Dict[str, Any]) -> httpx.Response:
        if spec["json"] is not None:
            return httpx.Response(spec["status"], json=spec["json"], headers=spec["headers"])
        if spec["text"] is not None:
            return httpx.Response(spec["status"], text=spec["text"], headers=spec["headers"])
        return httpx.Response(spec["status"], headers=spec["headers"])

    def handler(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        key = (request.method, request.url.path)
        queue = self._queues.get(key)
        if not queue:
            return httpx.Response(404, json={"message": f"нет мока для {key}"})
        spec = queue.pop(0) if len(queue) > 1 else queue[0]
        return self._build(spec)

    @property
    def last(self) -> httpx.Request:
        assert self.requests, "запросов не было"
        return self.requests[-1]

    def last_body(self) -> Any:
        return json.loads(self.last.content)


def _base_config(sandbox: bool, max_retries: Optional[int] = None) -> Configuration:
    config = Configuration.create("test_client_id", "test_client_secret", ACCOUNT_ID)
    config = config.sandbox() if sandbox else config.production()
    config = config.with_retry_base_delay(0)
    if max_retries is not None:
        config = config.with_max_retries(max_retries)
    return config


def make_client(
    router: MockRouter, sandbox: bool = False, max_retries: Optional[int] = None
) -> Client:
    """Синхронный клиент поверх ``httpx.MockTransport``."""
    transport = httpx.MockTransport(router.handler)
    config = _base_config(sandbox, max_retries).with_http_client(httpx.Client(transport=transport))
    return Client(config)


def make_async_client(
    router: MockRouter, sandbox: bool = False, max_retries: Optional[int] = None
) -> AsyncClient:
    """Асинхронный клиент поверх ``httpx.MockTransport``."""
    transport = httpx.MockTransport(router.handler)
    config = _base_config(sandbox, max_retries).with_async_client(
        httpx.AsyncClient(transport=transport)
    )
    return AsyncClient(config)


async def call(value: Any) -> Any:
    """Возвращает результат, дожидаясь его, если это awaitable (async-режим)."""
    if inspect.isawaitable(value):
        return await value
    return value


async def collect(iterator: Any) -> List[Any]:
    """Собирает элементы из синхронного или асинхронного итератора в список."""
    if hasattr(iterator, "__aiter__"):
        return [item async for item in iterator]
    return list(iterator)


async def aclose(client: Any) -> None:
    """Закрывает клиент (sync ``close`` или async ``aclose``)."""
    if hasattr(client, "aclose"):
        await client.aclose()
    else:
        client.close()


@pytest.fixture(params=["sync", "async"])
def mode(request: Any) -> str:
    """Параметризует тест двумя режимами: ``sync`` и ``async``."""
    return request.param


@pytest.fixture
async def clients(mode: str):  # type: ignore[no-untyped-def]
    """Фабрика клиентов выбранного режима с автоматическим закрытием."""
    created: List[Any] = []

    def factory(
        router: MockRouter, sandbox: bool = False, max_retries: Optional[int] = None
    ) -> Any:
        if mode == "async":
            client = make_async_client(router, sandbox, max_retries)
        else:
            client = make_client(router, sandbox, max_retries)
        created.append(client)
        return client

    yield factory

    for client in created:
        await aclose(client)
