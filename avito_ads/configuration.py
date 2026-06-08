"""Конфигурация клиента Авито Реклама.

Объект неизменяемый: методы ``with_*`` и ``production``/``sandbox`` возвращают
новый экземпляр, не меняя исходный. Одна и та же конфигурация подходит и для
синхронного :class:`~avito_ads.Client`, и для асинхронного
:class:`~avito_ads.AsyncClient`.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, replace
from typing import Optional

import httpx

from .auth.credentials import Credentials
from .auth.storage import AsyncTokenStorage, TokenStorage
from .exceptions import ConfigurationError

_HOST = "https://api.avito.ru"
_PRODUCTION_PREFIX = "ads"
_SANDBOX_PREFIX = "ads-sandbox"


@dataclass(frozen=True)
class Configuration:
    """Параметры подключения к API.

    Создавайте через :meth:`create`, далее настраивайте цепочкой ``with_*``.
    """

    client_id: str
    client_secret: str
    account_id: int
    path_prefix: str = _PRODUCTION_PREFIX
    timeout: float = 30.0
    max_retries: int = 4
    retry_base_delay_ms: int = 1000
    token_leeway: int = 60
    user_agent: str = "avito-ads-python/0.1.0"
    logger: Optional[logging.Logger] = None
    token_storage: Optional[TokenStorage] = None
    async_token_storage: Optional[AsyncTokenStorage] = None
    http_client: Optional[httpx.Client] = None
    async_client: Optional[httpx.AsyncClient] = None

    @classmethod
    def create(cls, client_id: str, client_secret: str, account_id: int) -> "Configuration":
        """Создаёт конфигурацию, проверяя обязательные поля.

        :raises ConfigurationError: при пустых учётных данных или ``account_id`` <= 0.
        """
        if not client_id:
            raise ConfigurationError("Не задан client_id.")
        if not client_secret:
            raise ConfigurationError("Не задан client_secret.")
        if account_id <= 0:
            raise ConfigurationError("account_id должен быть положительным целым числом.")
        return cls(client_id=client_id, client_secret=client_secret, account_id=account_id)

    # --- Окружения -----------------------------------------------------------

    def production(self) -> "Configuration":
        """Боевое окружение (``https://api.avito.ru/ads/``)."""
        return replace(self, path_prefix=_PRODUCTION_PREFIX)

    def sandbox(self) -> "Configuration":
        """Песочница (``https://api.avito.ru/ads-sandbox/``)."""
        return replace(self, path_prefix=_SANDBOX_PREFIX)

    # --- Настройки -----------------------------------------------------------

    def with_timeout(self, timeout: float) -> "Configuration":
        """Таймаут запроса, секунды."""
        return replace(self, timeout=timeout)

    def with_max_retries(self, max_retries: int) -> "Configuration":
        """Максимальное число повторов при 429/5xx/сетевых ошибках."""
        return replace(self, max_retries=max_retries)

    def with_retry_base_delay(self, retry_base_delay_ms: int) -> "Configuration":
        """Базовая задержка повтора, миллисекунды."""
        return replace(self, retry_base_delay_ms=retry_base_delay_ms)

    def with_token_leeway(self, token_leeway: int) -> "Configuration":
        """Запас на досрочное обновление токена, секунды."""
        return replace(self, token_leeway=token_leeway)

    def with_user_agent(self, user_agent: str) -> "Configuration":
        """Значение заголовка ``User-Agent``."""
        return replace(self, user_agent=user_agent)

    def with_logger(self, logger: logging.Logger) -> "Configuration":
        """Логгер для отладочных сообщений."""
        return replace(self, logger=logger)

    def with_token_storage(self, storage: TokenStorage) -> "Configuration":
        """Своё синхронное хранилище токена (для :class:`~avito_ads.Client`)."""
        return replace(self, token_storage=storage)

    def with_async_token_storage(self, storage: AsyncTokenStorage) -> "Configuration":
        """Своё асинхронное хранилище токена (для :class:`~avito_ads.AsyncClient`)."""
        return replace(self, async_token_storage=storage)

    def with_http_client(self, client: httpx.Client) -> "Configuration":
        """Готовый ``httpx.Client`` (например, с прокси/HTTP-2) — удобно для тестов."""
        return replace(self, http_client=client)

    def with_async_client(self, client: httpx.AsyncClient) -> "Configuration":
        """Готовый ``httpx.AsyncClient`` — удобно для тестов и тонкой настройки."""
        return replace(self, async_client=client)

    # --- Производные значения ------------------------------------------------

    @property
    def credentials(self) -> Credentials:
        return Credentials(self.client_id, self.client_secret)

    @property
    def base_uri(self) -> str:
        """Базовый адрес API с учётом окружения."""
        return f"{_HOST}/{self.path_prefix}/"

    @property
    def token_url(self) -> str:
        """Адрес эндпоинта получения токена (общий для prod и sandbox)."""
        return f"{_HOST}/token"
