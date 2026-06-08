"""SDK для публичного API кабинета Авито Реклама (Avito Ads).

Поддерживает два режима работы с одним и тем же API: синхронный и асинхронный.

Синхронный режим::

    from avito_ads import Client, Configuration

    config = Configuration.create("CLIENT_ID", "CLIENT_SECRET", 123456789).production()
    with Client(config) as client:
        balance = client.account.get_balance()
        print(balance.balance, balance.bonus_balance)

Асинхронный режим::

    import asyncio
    from avito_ads import AsyncClient, Configuration

    async def main() -> None:
        config = Configuration.create("CLIENT_ID", "CLIENT_SECRET", 123456789).production()
        async with AsyncClient(config) as client:
            balance = await client.account.get_balance()
            async for campaign in client.campaigns.iterate():
                print(campaign.id, campaign.name)

    asyncio.run(main())
"""

from __future__ import annotations

from ._async import AsyncClient
from ._sync import Client
from .auth import (
    AsyncTokenStorage,
    InMemoryAsyncTokenStorage,
    InMemoryTokenStorage,
    TokenStorage,
)
from .configuration import Configuration
from .contract_builder import ContractBuilder
from .enums import (
    CampaignPaymentModel,
    CampaignStatus,
    CampaignType,
    ContractAction,
    ContractCounterpartyType,
    ContractSubject,
    ContractType,
    CreativesStatus,
    GroupsStatus,
    LegalRole,
    LegalType,
    UserRole,
)
from .exceptions import (
    AccessDeniedError,
    ApiError,
    AuthenticationError,
    AvitoAdsError,
    BadRequestError,
    ConfigurationError,
    NetworkError,
    NotFoundError,
    RateLimitError,
    ServerError,
    ValidationError,
)
from .filters import (
    AdvertiserFilter,
    CampaignsFilter,
    ContractsFilter,
    CreativesFilter,
    DateRange,
    GroupsFilter,
)
from .pagination import ListRequest, PaginatedResult

__version__ = "0.1.0"

__all__ = [
    "__version__",
    # clients
    "Client",
    "AsyncClient",
    "Configuration",
    "ContractBuilder",
    # token storage
    "TokenStorage",
    "InMemoryTokenStorage",
    "AsyncTokenStorage",
    "InMemoryAsyncTokenStorage",
    # enums
    "LegalType",
    "LegalRole",
    "UserRole",
    "ContractType",
    "ContractSubject",
    "ContractAction",
    "ContractCounterpartyType",
    "CampaignPaymentModel",
    "CampaignType",
    "CampaignStatus",
    "GroupsStatus",
    "CreativesStatus",
    # exceptions
    "AvitoAdsError",
    "ConfigurationError",
    "ValidationError",
    "ApiError",
    "BadRequestError",
    "AuthenticationError",
    "AccessDeniedError",
    "NotFoundError",
    "RateLimitError",
    "ServerError",
    "NetworkError",
    # filters / pagination
    "DateRange",
    "AdvertiserFilter",
    "ContractsFilter",
    "CampaignsFilter",
    "GroupsFilter",
    "CreativesFilter",
    "ListRequest",
    "PaginatedResult",
]
