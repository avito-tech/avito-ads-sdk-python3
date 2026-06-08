"""Асинхронный клиент API Авито Реклама."""

from __future__ import annotations

import httpx

from ..auth.storage import AsyncTokenStorage, InMemoryAsyncTokenStorage
from ..configuration import Configuration
from .resources import (
    AsyncAccountResource,
    AsyncAdvertiserResource,
    AsyncCampaignResource,
    AsyncChildAccountResource,
    AsyncContractResource,
    AsyncCreativeResource,
    AsyncGroupResource,
    AsyncStatisticsResource,
    AsyncUserResource,
)
from .token_provider import AsyncTokenProvider
from .transport import AsyncHttpTransport


class AsyncClient:
    """Асинхронный клиент API Авито Реклама.

    Создаётся из той же :class:`~avito_ads.Configuration`, что и синхронный
    :class:`~avito_ads.Client`; имена ресурсов, методов и аргументов идентичны —
    разница только в ``await`` / ``async for`` / ``async with``.

    Рекомендуется использовать как асинхронный менеджер контекста::

        async with AsyncClient(config) as client:
            balance = await client.account.get_balance()
            async for campaign in client.campaigns.iterate():
                ...
    """

    def __init__(self, config: Configuration) -> None:
        self._config = config

        if config.async_client is not None:
            self._client = config.async_client
            self._owns_client = False
        else:
            self._client = httpx.AsyncClient(timeout=config.timeout)
            self._owns_client = True

        storage: AsyncTokenStorage = config.async_token_storage or InMemoryAsyncTokenStorage()
        self._token_provider = AsyncTokenProvider(
            client=self._client,
            credentials=config.credentials,
            token_url=config.token_url,
            storage=storage,
            leeway=config.token_leeway,
            timeout=config.timeout,
            user_agent=config.user_agent,
            logger=config.logger,
        )
        self._http = AsyncHttpTransport(
            client=self._client,
            base_uri=config.base_uri,
            token_provider=self._token_provider,
            max_retries=config.max_retries,
            retry_base_delay_ms=config.retry_base_delay_ms,
            timeout=config.timeout,
            user_agent=config.user_agent,
            logger=config.logger,
        )

        account_id = config.account_id
        self.account = AsyncAccountResource(self._http, account_id)
        self.child_accounts = AsyncChildAccountResource(self._http, account_id)
        self.advertisers = AsyncAdvertiserResource(self._http, account_id)
        self.contracts = AsyncContractResource(self._http, account_id)
        self.campaigns = AsyncCampaignResource(self._http, account_id)
        self.groups = AsyncGroupResource(self._http, account_id)
        self.creatives = AsyncCreativeResource(self._http, account_id)
        self.statistics = AsyncStatisticsResource(self._http, account_id)
        self.users = AsyncUserResource(self._http, account_id)

    @property
    def configuration(self) -> Configuration:
        return self._config

    async def aclose(self) -> None:
        """Закрывает HTTP-клиент, если он создан этим объектом."""
        if self._owns_client:
            await self._client.aclose()

    async def __aenter__(self) -> "AsyncClient":
        return self

    async def __aexit__(self, *_exc: object) -> None:
        await self.aclose()

    @property
    def transport(self) -> AsyncHttpTransport:
        return self._http

    @property
    def token_provider(self) -> AsyncTokenProvider:
        return self._token_provider
