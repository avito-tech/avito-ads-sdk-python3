"""Интеграция с FastAPI через зависимость (Depends).

FastAPI — асинхронный фреймворк, поэтому интеграция отдаёт асинхронный
:class:`~avito_ads.AsyncClient`. Один общий клиент создаётся при старте и
закрывается на завершении приложения.

Пример::

    from contextlib import asynccontextmanager
    from fastapi import Depends, FastAPI
    from avito_ads import AsyncClient
    from avito_ads.integrations.fastapi import AvitoAdsProvider

    avito = AvitoAdsProvider({
        "client_id": "...",
        "client_secret": "...",
        "account_id": 123456789,
        "environment": "production",
    })

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        yield
        await avito.aclose()

    app = FastAPI(lifespan=lifespan)

    @app.get("/balance")
    async def balance(client: AsyncClient = Depends(avito)):
        result = await client.account.get_balance()
        return {"balance": result.balance}
"""

from __future__ import annotations

from typing import Any, Mapping, Optional

from .. import AsyncClient
from ..auth.storage import AsyncTokenStorage
from ._common import build_configuration


class AvitoAdsProvider:
    """Фабрика-зависимость FastAPI, отдающая общий :class:`AsyncClient`.

    Экземпляр провайдера вызывается как зависимость (``Depends(provider)``) и
    возвращает один и тот же закэшированный асинхронный клиент. Не забудьте
    закрыть его на завершении приложения через :meth:`aclose`.
    """

    def __init__(
        self,
        settings: Mapping[str, Any],
        token_storage: Optional[AsyncTokenStorage] = None,
    ) -> None:
        self._config = build_configuration(settings)
        if token_storage is not None:
            self._config = self._config.with_async_token_storage(token_storage)
        self._client: Optional[AsyncClient] = None

    def __call__(self) -> AsyncClient:
        if self._client is None:
            self._client = AsyncClient(self._config)
        return self._client

    async def aclose(self) -> None:
        """Закрывает клиент, если он был создан."""
        if self._client is not None:
            await self._client.aclose()
