"""Синхронный клиент API Авито Реклама."""

from __future__ import annotations

import httpx

from ..auth.storage import InMemoryTokenStorage, TokenStorage
from ..configuration import Configuration
from .resources import (
    AccountResource,
    AdvertiserResource,
    CampaignResource,
    ChildAccountResource,
    ContractResource,
    CreativeResource,
    GroupResource,
    StatisticsResource,
    UserResource,
)
from .token_provider import SyncTokenProvider
from .transport import SyncHttpTransport


class Client:
    """Синхронный клиент API Авито Реклама.

    Создаётся из :class:`~avito_ads.Configuration` и предоставляет доступ к
    ресурсам. Все запросы выполняются от лица аккаунта из конфигурации.

    Поддерживает протокол менеджера контекста для освобождения соединений::

        with Client(config) as client:
            balance = client.account.get_balance()

    Пример::

        from avito_ads import Client, Configuration

        config = Configuration.create("CLIENT_ID", "CLIENT_SECRET", 123456789).production()
        client = Client(config)
        balance = client.account.get_balance()
    """

    def __init__(self, config: Configuration) -> None:
        self._config = config

        if config.http_client is not None:
            self._client = config.http_client
            self._owns_client = False
        else:
            self._client = httpx.Client(timeout=config.timeout)
            self._owns_client = True

        storage: TokenStorage = config.token_storage or InMemoryTokenStorage()
        self._token_provider = SyncTokenProvider(
            client=self._client,
            credentials=config.credentials,
            token_url=config.token_url,
            storage=storage,
            leeway=config.token_leeway,
            timeout=config.timeout,
            user_agent=config.user_agent,
            logger=config.logger,
        )
        self._http = SyncHttpTransport(
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
        self.account = AccountResource(self._http, account_id)
        self.child_accounts = ChildAccountResource(self._http, account_id)
        self.advertisers = AdvertiserResource(self._http, account_id)
        self.contracts = ContractResource(self._http, account_id)
        self.campaigns = CampaignResource(self._http, account_id)
        self.groups = GroupResource(self._http, account_id)
        self.creatives = CreativeResource(self._http, account_id)
        self.statistics = StatisticsResource(self._http, account_id)
        self.users = UserResource(self._http, account_id)

    @property
    def configuration(self) -> Configuration:
        return self._config

    def close(self) -> None:
        """Закрывает HTTP-клиент, если он создан этим объектом."""
        if self._owns_client:
            self._client.close()

    def __enter__(self) -> "Client":
        return self

    def __exit__(self, *_exc: object) -> None:
        self.close()

    @property
    def transport(self) -> SyncHttpTransport:
        return self._http

    @property
    def token_provider(self) -> SyncTokenProvider:
        return self._token_provider
