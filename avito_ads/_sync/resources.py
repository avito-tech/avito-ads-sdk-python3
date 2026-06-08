"""Синхронные ресурсы API — тонкие обёртки над операциями ядра.

Каждый метод строит операцию из :mod:`avito_ads._core.operations` (единый
источник правды о пути/теле/разборе) и исполняет её через синхронный транспорт.
"""

from __future__ import annotations

from typing import Any, Dict, Iterator, List, Optional, Union

from .._core import operations as ops
from .._core.operations import FilterType
from ..contract_builder import ContractBuilder
from ..enums import UserRole
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
    EntityStatistic,
    Group,
    User,
)
from ..pagination import DEFAULT_LIMIT, PaginatedResult, iterate_pages
from .transport import SyncHttpTransport


class _SyncResource:
    """Базовый синхронный ресурс: транспорт и идентификатор аккаунта."""

    def __init__(self, http: SyncHttpTransport, account_id: int) -> None:
        self._http = http
        self._account_id = account_id


class AccountResource(_SyncResource):
    """Реквизиты, баланс, создание тестового аккаунта."""

    def get(self) -> Account:
        """Реквизиты текущего аккаунта (``GET /v1/account/{accountID}``)."""
        return self._http.execute(ops.get_account(self._account_id))

    def get_balance(self) -> Balance:
        """Баланс текущего аккаунта (``GET /v1/account/{accountID}/balance``)."""
        return self._http.execute(ops.get_balance(self._account_id))

    def create_sandbox_account(
        self,
        inn: str,
        short_name: str,
        long_name: str,
        ogrn: str,
        legal_address: str,
        actual_address: str,
        contact: Dict[str, Any],
        kpp: Optional[str] = None,
        legal_type: Optional[str] = None,
    ) -> CreatedAccount:
        """Создаёт тестовый аккаунт (только в песочнице, ``POST /v1/account/{accountID}``)."""
        return self._http.execute(
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


class ChildAccountResource(_SyncResource):
    """Дочерние аккаунты и переводы средств/бонусов."""

    def list(self) -> List[ChildAccount]:
        """Список дочерних аккаунтов (``GET /v1/account/{accountID}/children``)."""
        return self._http.execute(ops.list_children(self._account_id, with_balances=False))

    def list_with_balances(self) -> List[ChildAccount]:
        """Список дочерних аккаунтов с балансами."""
        return self._http.execute(ops.list_children(self._account_id, with_balances=True))

    def create_nonpayer_child(
        self, short_name: str, is_self_advertising_enabled: bool
    ) -> CreatedChildAccount:
        """Создаёт дочерний аккаунт-непокупатель."""
        return self._http.execute(
            ops.create_nonpayer_child(self._account_id, short_name, is_self_advertising_enabled)
        )

    def transfer_funds(self, account_id_to: int, amount: int) -> None:
        """Перевод денежных средств (сумма >= 1)."""
        self._http.execute(ops.transfer(self._account_id, "funds-transfer", account_id_to, amount))

    def transfer_bonus(self, account_id_to: int, amount: int) -> None:
        """Перевод бонусов (сумма >= 1)."""
        self._http.execute(ops.transfer(self._account_id, "bonus-transfer", account_id_to, amount))


class AdvertiserResource(_SyncResource):
    """Рекламодатели."""

    def create(
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
        return self._http.execute(
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

    def list(
        self, filter: FilterType = None, limit: int = DEFAULT_LIMIT, page: int = 1
    ) -> PaginatedResult[Advertiser]:
        """Список рекламодателей (``POST /v1/account/{accountID}/advertisers``)."""
        request = ops.make_list_request(filter, limit, page)
        return self._http.execute(ops.list_advertisers(self._account_id, request))

    def iterate(
        self, filter: FilterType = None, limit: int = DEFAULT_LIMIT
    ) -> Iterator[Advertiser]:
        """Перебор всех рекламодателей по всем страницам."""
        request = ops.make_list_request(filter, limit, 1)
        return iterate_pages(
            lambda req: self._http.execute(ops.list_advertisers(self._account_id, req)), request
        )


class ContractResource(_SyncResource):
    """Договоры."""

    def create(self, contract: Union[ContractBuilder, Dict[str, Any]]) -> CreatedContract:
        """Создаёт договор (билдер или готовый словарь)."""
        body = ops.contract_body(contract)
        return self._http.execute(ops.create_contract(self._account_id, body))

    def list(
        self, filter: FilterType = None, limit: int = DEFAULT_LIMIT, page: int = 1
    ) -> PaginatedResult[Contract]:
        """Список договоров (``POST /v1/account/{accountID}/contracts``)."""
        request = ops.make_list_request(filter, limit, page)
        return self._http.execute(ops.list_contracts(self._account_id, request))

    def iterate(self, filter: FilterType = None, limit: int = DEFAULT_LIMIT) -> Iterator[Contract]:
        """Перебор всех договоров по всем страницам."""
        request = ops.make_list_request(filter, limit, 1)
        return iterate_pages(
            lambda req: self._http.execute(ops.list_contracts(self._account_id, req)), request
        )


class CampaignResource(_SyncResource):
    """Кампании."""

    def list(
        self, filter: FilterType = None, limit: int = DEFAULT_LIMIT, page: int = 1
    ) -> PaginatedResult[Campaign]:
        """Список кампаний (``POST /v1/account/{accountID}/campaigns``)."""
        request = ops.make_list_request(filter, limit, page)
        return self._http.execute(ops.list_campaigns(self._account_id, request))

    def iterate(self, filter: FilterType = None, limit: int = DEFAULT_LIMIT) -> Iterator[Campaign]:
        """Перебор всех кампаний по всем страницам."""
        request = ops.make_list_request(filter, limit, 1)
        return iterate_pages(
            lambda req: self._http.execute(ops.list_campaigns(self._account_id, req)), request
        )


class GroupResource(_SyncResource):
    """Группы объявлений (изменение бюджета/ставки — только ручная ставка)."""

    def list(
        self, filter: FilterType = None, limit: int = DEFAULT_LIMIT, page: int = 1
    ) -> PaginatedResult[Group]:
        """Список групп (``POST /v1/account/{accountID}/groups``)."""
        request = ops.make_list_request(filter, limit, page)
        return self._http.execute(ops.list_groups(self._account_id, request))

    def iterate(self, filter: FilterType = None, limit: int = DEFAULT_LIMIT) -> Iterator[Group]:
        """Перебор всех групп по всем страницам."""
        request = ops.make_list_request(filter, limit, 1)
        return iterate_pages(
            lambda req: self._http.execute(ops.list_groups(self._account_id, req)), request
        )

    def change_budget(self, group_id: int, budget: int) -> None:
        """Изменить бюджет группы (значение >= 1)."""
        self._http.execute(ops.change_group_budget(self._account_id, group_id, budget))

    def change_price(self, group_id: int, price: int) -> None:
        """Изменить ставку группы (значение >= 1)."""
        self._http.execute(ops.change_group_price(self._account_id, group_id, price))


class CreativeResource(_SyncResource):
    """Креативы."""

    def list(
        self, filter: FilterType = None, limit: int = DEFAULT_LIMIT, page: int = 1
    ) -> PaginatedResult[Creative]:
        """Список креативов (``POST /v1/account/{accountID}/creatives``)."""
        request = ops.make_list_request(filter, limit, page)
        return self._http.execute(ops.list_creatives(self._account_id, request))

    def iterate(self, filter: FilterType = None, limit: int = DEFAULT_LIMIT) -> Iterator[Creative]:
        """Перебор всех креативов по всем страницам."""
        request = ops.make_list_request(filter, limit, 1)
        return iterate_pages(
            lambda req: self._http.execute(ops.list_creatives(self._account_id, req)), request
        )


class StatisticsResource(_SyncResource):
    """Статистика (период <= 100 дней, даты ``YYYY-MM-DD``)."""

    def campaign(
        self, campaign_id: int, date_from: str, date_to: str
    ) -> CampaignStatisticResult:
        """Статистика по кампании со сводками по группам и креативам."""
        return self._http.execute(
            ops.campaign_statistics(self._account_id, campaign_id, date_from, date_to)
        )

    def groups(
        self, campaign_id: int, date_from: str, date_to: str, group_ids: List[int]
    ) -> List[EntityStatistic]:
        """Статистика по группам кампании."""
        return self._http.execute(
            ops.group_statistics(self._account_id, campaign_id, date_from, date_to, group_ids)
        )

    def creatives(
        self, campaign_id: int, date_from: str, date_to: str, creative_ids: List[int]
    ) -> List[EntityStatistic]:
        """Статистика по креативам кампании."""
        return self._http.execute(
            ops.creative_statistics(self._account_id, campaign_id, date_from, date_to, creative_ids)
        )


class UserResource(_SyncResource):
    """Пользователи аккаунта."""

    def list(self) -> List[User]:
        """Список пользователей (``GET /v1/account/{accountID}/users``)."""
        return self._http.execute(ops.list_users(self._account_id))

    def add(self, user_id: int, role: Union[str, UserRole]) -> None:
        """Добавить пользователя (``POST /v1/account/{accountID}/add-user``)."""
        self._http.execute(ops.add_user(self._account_id, user_id, role))

    def set_role(self, user_id: int, role: Union[str, UserRole]) -> None:
        """Изменить роль пользователя (``POST /v1/account/{accountID}/set-user-role``)."""
        self._http.execute(ops.set_user_role(self._account_id, user_id, role))

    def delete(self, user_id: int) -> None:
        """Удалить пользователя (``DELETE /v1/account/{accountID}/delete-user/{userID}``)."""
        self._http.execute(ops.delete_user(self._account_id, user_id))


# Совместимость с ListRequest-импортом в типах (не используется напрямую здесь).
__all__ = [
    "AccountResource",
    "ChildAccountResource",
    "AdvertiserResource",
    "ContractResource",
    "CampaignResource",
    "GroupResource",
    "CreativeResource",
    "StatisticsResource",
    "UserResource",
]
