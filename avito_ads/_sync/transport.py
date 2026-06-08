"""Синхронный транспортный слой на ``httpx.Client``.

Вся содержательная логика (заголовки, разбор, ошибки, политика повторов) берётся
из :mod:`avito_ads._core.transport`; здесь — только цикл выполнения с реальным
вводом-выводом и паузами ``time.sleep``.
"""

from __future__ import annotations

import logging
import time
from typing import Any, Callable, Dict, Optional, TypeVar

import httpx

from .._core import transport as core
from .._core.operations import Operation
from .._core.response import ApiResponse
from ..exceptions import NetworkError
from .token_provider import SyncTokenProvider

T = TypeVar("T")


class SyncHttpTransport:
    """Выполняет HTTP-запросы к API с авторизацией, повторами и разбором ответа."""

    def __init__(
        self,
        client: httpx.Client,
        base_uri: str,
        token_provider: SyncTokenProvider,
        max_retries: int = 4,
        retry_base_delay_ms: int = 1000,
        timeout: float = 30.0,
        user_agent: str = "avito-ads-python/0.1.0",
        logger: Optional[logging.Logger] = None,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        self._client = client
        self._base_uri = base_uri.rstrip("/") + "/"
        self._token_provider = token_provider
        self._max_retries = max_retries
        self._retry_base_delay_ms = retry_base_delay_ms
        self._timeout = timeout
        self._user_agent = user_agent
        self._logger = logger
        self._sleep = sleep

    def execute(self, operation: "Operation[T]") -> T:
        """Исполняет операцию и возвращает разобранный результат."""
        response = self.request(operation.method, operation.path, operation.body)
        return operation.parse(response)

    def request(
        self, method: str, path: str, body: Optional[Dict[str, Any]] = None
    ) -> ApiResponse:
        url = self._base_uri + path.lstrip("/")
        attempt = 0
        token_refreshed = False

        while True:
            token = self._token_provider.get_token()
            headers = core.build_headers(token.authorization_header(), body is not None)
            headers["User-Agent"] = self._user_agent

            try:
                response = self._client.request(
                    method,
                    url,
                    json=body if body is not None else None,
                    headers=headers,
                    timeout=self._timeout,
                )
            except httpx.RequestError as exc:
                if attempt < self._max_retries:
                    attempt += 1
                    self._sleep(
                        core.backoff_delay_seconds(attempt, self._retry_base_delay_ms, None)
                    )
                    continue
                raise NetworkError(f"Сетевая ошибка при запросе {method} {path}: {exc}") from exc

            status = response.status_code
            plan = core.plan_after_response(status, attempt, self._max_retries, token_refreshed)

            if plan.action == core.REFRESH:
                token_refreshed = True
                self._token_provider.forget_token()
                if self._logger is not None:
                    self._logger.info("Получен 401, токен сброшен, повтор запроса.")
                continue
            if plan.action == core.WAIT:
                attempt += 1
                self._sleep(
                    core.backoff_delay_seconds(
                        attempt,
                        self._retry_base_delay_ms,
                        core.retry_after_seconds(response.headers.get),
                    )
                )
                continue
            if plan.action == core.RAISE:
                data = core.parse_body(response.content, response.json)
                raise core.error_from_response(
                    status, data, response.headers.get, response.request, response
                )

            return core.make_api_response(
                status, response.headers.get, response.content, response.json
            )
