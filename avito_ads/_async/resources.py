"""Асинхронные ресурсы API — зеркало синхронных, отличаются только ``await``.

Каждый метод строит ту же операцию из :mod:`avito_ads._core.operations`, что и
синхронный аналог, и исполняет её через асинхронный транспорт.
"""

from __future__ import annotations

from typing import Any, AsyncIterator, Dict, List, Optional, Union

from .._core import operations as ops
from .._core.operations import FilterType
from ..contract_builder import ContractBuilder
from ..enums import LegalType, UserRole
from ..models import (
    Account,
    Advertiser,
    Balance,
    Campaign,
    CampaignStatisticResult,
    ChildAccount,
    Contract,
    CreatedAccount,
    CreatedAdvertiser,
    CreatedChildAccount,
    CreatedContract,
    Creative,
    CreativeStatistic,
    Group,
    GroupStatistic,
    User,
)
from ..pagination import DEFAULT_LIMIT, PaginatedResult, iterate_pages_async
from .transport import AsyncHttpTransport


class _AsyncResource:
    """Базовый асинхронный ресурс: транспорт и идентификатор аккаунта."""

    def __init__(self, http: AsyncHttpTransport, account_id: int) -> None:
        self._http = http
        self._account_id = account_id


class AsyncAccountResource(_AsyncResource):
    """Реквизиты, баланс, создание тестового аккаунта."""

    async def get(self) -> Account:
        """Реквизиты текущего аккаунта (``GET /v1/account/{accountID}``)."""
        return await self._http.execute(ops.get_account(self._account_id))

    async def get_balance(self) -> Balance:
        """Баланс текущего аккаунта (``GET /v1/account/{accountID}/balance``)."""
        return await self._http.execute(ops.get_balance(self._account_id))

    async def create_sandbox_account(
        self,
        inn: str,
        short_name: str,
        long_name: str,
        ogrn: str,
        legal_address: str,
        actual_address: Optional[str],
        contact: Dict[str, Any],
        kpp: Optional[str] = None,
        legal_type: Union[str, LegalType, None] = None,
    ) -> CreatedAccount:
        """Создаёт тестовый аккаунт (только в песочнице, ``POST /v1/account/{accountID}``).

        ``legal_type`` (``"ul"``/``"ip"``, :class:`~avito_ads.enums.LegalType`)
        обязателен: без него бросается ``ValidationError`` до запроса. Значение по
        умолчанию ``None`` оставлено только ради порядка аргументов.
        ``actual_address`` можно передать ``None`` — API возьмёт ``legal_address``.

        Ответы ``200`` и ``207`` (аккаунт создан, но часть sandbox-данных не
        подготовилась) — успех; предупреждения — в ``CreatedAccount.warnings``.
        """
        return await self._http.execute(
            ops.create_sandbox_account(
                self._account_id,
                inn,
                short_name,
                long_name,
                ogrn,
                legal_address,
                actual_address,
                contact,
                kpp,
                legal_type,
            )
        )


class AsyncChildAccountResource(_AsyncResource):
    """Дочерние аккаунты и переводы средств/бонусов."""

    async def list(self) -> List[ChildAccount]:
        """Список дочерних аккаунтов (``GET /v1/account/{accountID}/children``)."""
        return await self._http.execute(ops.list_children(self._account_id, with_balances=False))

    async def list_with_balances(self) -> List[ChildAccount]:
        """Список дочерних аккаунтов с балансами."""
        return await self._http.execute(ops.list_children(self._account_id, with_balances=True))

    async def create_nonpayer_child(
        self, short_name: str, is_self_advertising_enabled: bool
    ) -> CreatedChildAccount:
        """Создаёт дочерний аккаунт-непокупатель."""
        return await self._http.execute(
            ops.create_nonpayer_child(self._account_id, short_name, is_self_advertising_enabled)
        )

    async def transfer_funds(self, account_id_to: int, amount: int) -> None:
        """Перевод денежных средств (сумма >= 1)."""
        await self._http.execute(
            ops.transfer(self._account_id, "funds-transfer", account_id_to, amount)
        )

    async def transfer_bonus(self, account_id_to: int, amount: int) -> None:
        """Перевод бонусов (сумма >= 1)."""
        await self._http.execute(
            ops.transfer(self._account_id, "bonus-transfer", account_id_to, amount)
        )


class AsyncAdvertiserResource(_AsyncResource):
    """Рекламодатели."""

    async def create(
        self,
        inn: str,
        short_name: str,
        long_name: str,
        ogrn: str,
        legal_address: str,
        actual_address: str,
        legal_role: str,
        legal_type: str,
        kpp: Optional[str] = None,
    ) -> CreatedAdvertiser:
        """Создаёт рекламодателя (``POST /v1/account/{accountID}/create-advertiser``)."""
        return await self._http.execute(
            ops.create_advertiser(
                self._account_id,
                inn,
                short_name,
                long_name,
                ogrn,
                legal_address,
                actual_address,
                legal_role,
                legal_type,
                kpp,
            )
        )

    async def list(
        self, filter: FilterType = None, limit: int = DEFAULT_LIMIT, page: int = 1
    ) -> PaginatedResult[Advertiser]:
        """Список рекламодателей (``POST /v1/account/{accountID}/advertisers``)."""
        request = ops.make_list_request(filter, limit, page)
        return await self._http.execute(ops.list_advertisers(self._account_id, request))

    def iterate(
        self, filter: FilterType = None, limit: int = DEFAULT_LIMIT
    ) -> AsyncIterator[Advertiser]:
        """Асинхронный перебор всех рекламодателей по всем страницам."""
        request = ops.make_list_request(filter, limit, 1)

        async def loader(req: Any) -> PaginatedResult[Advertiser]:
            return await self._http.execute(ops.list_advertisers(self._account_id, req))

        return iterate_pages_async(loader, request)


class AsyncContractResource(_AsyncResource):
    """Договоры."""

    async def create(self, contract: Union[ContractBuilder, Dict[str, Any]]) -> CreatedContract:
        """Создаёт договор (билдер или готовый словарь)."""
        body = ops.contract_body(contract)
        return await self._http.execute(ops.create_contract(self._account_id, body))

    async def list(
        self, filter: FilterType = None, limit: int = DEFAULT_LIMIT, page: int = 1
    ) -> PaginatedResult[Contract]:
        """Список договоров (``POST /v1/account/{accountID}/contracts``)."""
        request = ops.make_list_request(filter, limit, page)
        return await self._http.execute(ops.list_contracts(self._account_id, request))

    def iterate(
        self, filter: FilterType = None, limit: int = DEFAULT_LIMIT
    ) -> AsyncIterator[Contract]:
        """Асинхронный перебор всех договоров по всем страницам."""
        request = ops.make_list_request(filter, limit, 1)

        async def loader(req: Any) -> PaginatedResult[Contract]:
            return await self._http.execute(ops.list_contracts(self._account_id, req))

        return iterate_pages_async(loader, request)


class AsyncCampaignResource(_AsyncResource):
    """Кампании."""

    async def list(
        self, filter: FilterType = None, limit: int = DEFAULT_LIMIT, page: int = 1
    ) -> PaginatedResult[Campaign]:
        """Список кампаний (``POST /v1/account/{accountID}/campaigns``)."""
        request = ops.make_list_request(filter, limit, page)
        return await self._http.execute(ops.list_campaigns(self._account_id, request))

    def iterate(
        self, filter: FilterType = None, limit: int = DEFAULT_LIMIT
    ) -> AsyncIterator[Campaign]:
        """Асинхронный перебор всех кампаний по всем страницам."""
        request = ops.make_list_request(filter, limit, 1)

        async def loader(req: Any) -> PaginatedResult[Campaign]:
            return await self._http.execute(ops.list_campaigns(self._account_id, req))

        return iterate_pages_async(loader, request)


class AsyncGroupResource(_AsyncResource):
    """Группы объявлений (изменение бюджета/ставки — только ручная ставка)."""

    async def list(
        self, filter: FilterType = None, limit: int = DEFAULT_LIMIT, page: int = 1
    ) -> PaginatedResult[Group]:
        """Список групп (``POST /v1/account/{accountID}/groups``)."""
        request = ops.make_list_request(filter, limit, page)
        return await self._http.execute(ops.list_groups(self._account_id, request))

    def iterate(
        self, filter: FilterType = None, limit: int = DEFAULT_LIMIT
    ) -> AsyncIterator[Group]:
        """Асинхронный перебор всех групп по всем страницам."""
        request = ops.make_list_request(filter, limit, 1)

        async def loader(req: Any) -> PaginatedResult[Group]:
            return await self._http.execute(ops.list_groups(self._account_id, req))

        return iterate_pages_async(loader, request)

    async def change_budget(self, group_id: int, budget: int) -> None:
        """Изменить бюджет группы (значение >= 1).

        :raises ConflictError: 409 — группу изменили параллельно; перечитайте её и повторите.
        """
        await self._http.execute(ops.change_group_budget(self._account_id, group_id, budget))

    async def change_price(self, group_id: int, price: int) -> None:
        """Изменить ставку группы (значение >= 1).

        :raises ConflictError: 409 — группу изменили параллельно; перечитайте её и повторите.
        """
        await self._http.execute(ops.change_group_price(self._account_id, group_id, price))


class AsyncCreativeResource(_AsyncResource):
    """Креативы."""

    async def list(
        self, filter: FilterType = None, limit: int = DEFAULT_LIMIT, page: int = 1
    ) -> PaginatedResult[Creative]:
        """Список креативов (``POST /v1/account/{accountID}/creatives``)."""
        request = ops.make_list_request(filter, limit, page)
        return await self._http.execute(ops.list_creatives(self._account_id, request))

    def iterate(
        self, filter: FilterType = None, limit: int = DEFAULT_LIMIT
    ) -> AsyncIterator[Creative]:
        """Асинхронный перебор всех креативов по всем страницам."""
        request = ops.make_list_request(filter, limit, 1)

        async def loader(req: Any) -> PaginatedResult[Creative]:
            return await self._http.execute(ops.list_creatives(self._account_id, req))

        return iterate_pages_async(loader, request)


class AsyncStatisticsResource(_AsyncResource):
    """Статистика (период <= 100 дней, даты ``YYYY-MM-DD``)."""

    async def campaign(
        self, campaign_id: int, date_from: str, date_to: str
    ) -> CampaignStatisticResult:
        """Статистика по кампании со сводками по группам и креативам."""
        return await self._http.execute(
            ops.campaign_statistics(self._account_id, campaign_id, date_from, date_to)
        )

    async def groups(
        self, campaign_id: int, date_from: str, date_to: str, group_ids: List[int]
    ) -> List[GroupStatistic]:
        """Статистика по группам кампании."""
        return await self._http.execute(
            ops.group_statistics(self._account_id, campaign_id, date_from, date_to, group_ids)
        )

    async def creatives(
        self, campaign_id: int, date_from: str, date_to: str, creative_ids: List[int]
    ) -> List[CreativeStatistic]:
        """Статистика по креативам кампании."""
        return await self._http.execute(
            ops.creative_statistics(
                self._account_id, campaign_id, date_from, date_to, creative_ids
            )
        )


class AsyncUserResource(_AsyncResource):
    """Пользователи аккаунта."""

    async def list(self) -> List[User]:
        """Список пользователей (``GET /v1/account/{accountID}/users``)."""
        return await self._http.execute(ops.list_users(self._account_id))

    async def add(self, user_id: int, role: Union[str, UserRole]) -> None:
        """Добавить пользователя (``POST /v1/account/{accountID}/add-user``)."""
        await self._http.execute(ops.add_user(self._account_id, user_id, role))

    async def set_role(self, user_id: int, role: Union[str, UserRole]) -> None:
        """Изменить роль пользователя (``POST /v1/account/{accountID}/set-user-role``)."""
        await self._http.execute(ops.set_user_role(self._account_id, user_id, role))

    async def delete(self, user_id: int) -> None:
        """Удалить пользователя (``DELETE /v1/account/{accountID}/delete-user/{userID}``)."""
        await self._http.execute(ops.delete_user(self._account_id, user_id))


__all__ = [
    "AsyncAccountResource",
    "AsyncChildAccountResource",
    "AsyncAdvertiserResource",
    "AsyncContractResource",
    "AsyncCampaignResource",
    "AsyncGroupResource",
    "AsyncCreativeResource",
    "AsyncStatisticsResource",
    "AsyncUserResource",
]
