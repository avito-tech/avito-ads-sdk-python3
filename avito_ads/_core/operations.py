"""Описание операций API — единый источник правды о пути, теле и разборе ответа.

Каждая операция (:class:`Operation`) знает HTTP-метод, путь, тело запроса и
функцию разбора ответа в типизированную модель. И синхронные, и асинхронные
ресурсы строят ровно эти операции и исполняют их через свой транспорт —
поэтому путь, тело и разбор не дублируются и не расходятся между режимами.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable, Dict, Generic, List, Optional, Type, TypeVar, Union

from ..contract_builder import ContractBuilder
from ..enums import LegalType, UserRole
from ..exceptions import ConfigurationError, ValidationError
from ..filters import BaseFilter
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
    EntityStatistic,
    Group,
    GroupStatistic,
    User,
)
from ..pagination import DEFAULT_LIMIT, ListRequest, PaginatedResult
from .response import ApiResponse

T = TypeVar("T")
S = TypeVar("S", bound=EntityStatistic)

FilterType = Union[Dict[str, Any], BaseFilter, None]


@dataclass(frozen=True)
class Operation(Generic[T]):
    """Спецификация одного запроса к API.

    :param method: HTTP-метод (``GET``/``POST``/``DELETE``).
    :param path: путь относительно базового URI (без ведущего слэша).
    :param body: тело запроса (сериализуется в JSON) либо ``None``.
    :param parse: функция разбора :class:`ApiResponse` в результат.
    """

    method: str
    path: str
    body: Optional[Dict[str, Any]]
    parse: Callable[[ApiResponse], T]


def account_path(account_id: int, suffix: str = "") -> str:
    """Строит путь вида ``v1/account/{accountID}`` + необязательный суффикс."""
    base = f"v1/account/{account_id}"
    return f"{base}/{suffix}" if suffix else base


def make_list_request(filter_: FilterType, limit: int, page: int) -> ListRequest:
    """Нормализует фильтр (словарь/объект-фильтр/None) в :class:`ListRequest`."""
    if isinstance(filter_, BaseFilter):
        filter_dict = filter_.to_dict()
    elif filter_ is None:
        filter_dict = {}
    else:
        filter_dict = filter_
    return ListRequest(filter=filter_dict, limit=limit, page=page)


def _paginate(
    response: ApiResponse,
    items_key: str,
    request: ListRequest,
    factory: Callable[[Dict[str, Any]], T],
) -> "PaginatedResult[T]":
    data = response.data
    total = int(data.get("total", 0) or 0)
    rows = data.get(items_key, []) or []
    items: List[T] = [factory(row) for row in rows if isinstance(row, dict)]
    return PaginatedResult(
        total=total,
        items=items,
        page=request.page,
        limit=request.limit,
        api_point_balance=response.api_point_balance,
    )


def _list_operation(
    account_id: int,
    suffix: str,
    items_key: str,
    factory: Callable[[Dict[str, Any]], T],
    request: ListRequest,
) -> "Operation[PaginatedResult[T]]":
    """Строит операцию постраничной выборки (``POST`` с телом ListRequest)."""

    def parse(response: ApiResponse) -> "PaginatedResult[T]":
        return _paginate(response, items_key, request, factory)

    return Operation("POST", account_path(account_id, suffix), request.to_dict(), parse)


def _entities(rows: object, model: Type[S]) -> List[S]:
    if not isinstance(rows, list):
        return []
    return [model.from_dict(row) for row in rows if isinstance(row, dict)]


# --- Account ----------------------------------------------------------------


def get_account(account_id: int) -> "Operation[Account]":
    def parse(response: ApiResponse) -> Account:
        data = response.data
        account = data["account"] if isinstance(data.get("account"), dict) else data
        return Account.from_dict(account)

    return Operation("GET", account_path(account_id), None, parse)


def get_balance(account_id: int) -> "Operation[Balance]":
    return Operation(
        "GET", account_path(account_id, "balance"), None, lambda r: Balance.from_dict(r.data)
    )


def create_sandbox_account(
    account_id: int,
    inn: str,
    short_name: str,
    long_name: str,
    ogrn: str,
    legal_address: str,
    actual_address: Optional[str],
    contact: Dict[str, Any],
    kpp: Optional[str] = None,
    legal_type: Union[str, LegalType, None] = None,
) -> "Operation[CreatedAccount]":
    if not contact:
        raise ConfigurationError(
            "Для создания аккаунта необходимо передать контактное лицо (contact)."
        )
    if legal_type is None:
        raise ValidationError(
            "Для создания аккаунта необходимо передать тип юрлица (legal_type: 'ul' или 'ip')."
        )
    body: Dict[str, Any] = {
        "inn": inn,
        "shortName": short_name,
        "longName": long_name,
        "ogrn": ogrn,
        "legalAddress": legal_address,
        "legalType": LegalType.assert_valid(legal_type),
        "contact": contact,
    }
    if actual_address is not None:
        body["actualAddress"] = actual_address
    if kpp is not None:
        body["kpp"] = kpp
    return Operation(
        "POST", account_path(account_id), body, lambda r: CreatedAccount.from_dict(r.data)
    )


# --- Child accounts ---------------------------------------------------------


def list_children(account_id: int, with_balances: bool) -> "Operation[List[ChildAccount]]":
    suffix = "children-with-balances" if with_balances else "children"

    def parse(response: ApiResponse) -> List[ChildAccount]:
        rows = response.data.get("children", []) or []
        return [ChildAccount.from_dict(row) for row in rows if isinstance(row, dict)]

    return Operation("GET", account_path(account_id, suffix), None, parse)


def create_nonpayer_child(
    account_id: int, short_name: str, is_self_advertising_enabled: bool
) -> "Operation[CreatedChildAccount]":
    body = {"shortName": short_name, "isSelfAdvertisingEnabled": is_self_advertising_enabled}
    return Operation(
        "POST",
        account_path(account_id, "create-nonpayer-child-account"),
        body,
        lambda r: CreatedChildAccount.from_dict(r.data),
    )


def transfer(account_id: int, suffix: str, account_id_to: int, amount: int) -> "Operation[None]":
    if amount < 1:
        raise ValidationError(f"Сумма перевода должна быть не менее 1, передано {amount}.")
    body = {"accountIdTo": account_id_to, "amount": amount}
    return Operation("POST", account_path(account_id, suffix), body, lambda _r: None)


# --- Advertisers ------------------------------------------------------------


def create_advertiser(
    account_id: int,
    inn: str,
    short_name: str,
    long_name: str,
    ogrn: str,
    legal_address: str,
    actual_address: str,
    legal_role: str,
    legal_type: str,
    kpp: Optional[str] = None,
) -> "Operation[CreatedAdvertiser]":
    body: Dict[str, Any] = {
        "inn": inn,
        "shortName": short_name,
        "longName": long_name,
        "ogrn": ogrn,
        "legalAddress": legal_address,
        "actualAddress": actual_address,
        "legalRole": legal_role,
        "legalType": legal_type,
    }
    if kpp is not None:
        body["kpp"] = kpp
    return Operation(
        "POST",
        account_path(account_id, "create-advertiser"),
        body,
        lambda r: CreatedAdvertiser.from_dict(r.data),
    )


def list_advertisers(
    account_id: int, request: ListRequest
) -> "Operation[PaginatedResult[Advertiser]]":
    return _list_operation(account_id, "advertisers", "advertisers", Advertiser.from_dict, request)


# --- Contracts --------------------------------------------------------------


def contract_body(contract: Union[ContractBuilder, Dict[str, Any]]) -> Dict[str, Any]:
    """Возвращает тело договора из билдера (с проверкой правил) или из словаря."""
    return contract.build() if isinstance(contract, ContractBuilder) else contract


def create_contract(account_id: int, body: Dict[str, Any]) -> "Operation[CreatedContract]":
    return Operation(
        "POST",
        account_path(account_id, "create-contract"),
        body,
        lambda r: CreatedContract.from_dict(r.data),
    )


def list_contracts(
    account_id: int, request: ListRequest
) -> "Operation[PaginatedResult[Contract]]":
    return _list_operation(account_id, "contracts", "contracts", Contract.from_dict, request)


# --- Campaigns / Groups / Creatives -----------------------------------------


def list_campaigns(
    account_id: int, request: ListRequest
) -> "Operation[PaginatedResult[Campaign]]":
    return _list_operation(account_id, "campaigns", "campaigns", Campaign.from_dict, request)


def list_groups(account_id: int, request: ListRequest) -> "Operation[PaginatedResult[Group]]":
    return _list_operation(account_id, "groups", "groups", Group.from_dict, request)


def list_creatives(
    account_id: int, request: ListRequest
) -> "Operation[PaginatedResult[Creative]]":
    return _list_operation(account_id, "creatives", "creatives", Creative.from_dict, request)


def change_group_budget(account_id: int, group_id: int, budget: int) -> "Operation[None]":
    """Изменение бюджета группы; при конфликте версий API отвечает 409 (``ConflictError``)."""
    if budget < 1:
        raise ValidationError(f"Бюджет должен быть не менее 1, передано {budget}.")
    return Operation(
        "POST",
        account_path(account_id, f"group/{group_id}/change-budget"),
        {"budget": budget},
        lambda _r: None,
    )


def change_group_price(account_id: int, group_id: int, price: int) -> "Operation[None]":
    """Изменение ставки группы; при конфликте версий API отвечает 409 (``ConflictError``)."""
    if price < 1:
        raise ValidationError(f"Ставка должна быть не менее 1, передано {price}.")
    return Operation(
        "POST",
        account_path(account_id, f"group/{group_id}/change-price"),
        {"price": price},
        lambda _r: None,
    )


# --- Statistics -------------------------------------------------------------

_MAX_PERIOD_DAYS = 100


def _assert_period(date_from: str, date_to: str) -> None:
    try:
        start = datetime.strptime(date_from, "%Y-%m-%d")
        end = datetime.strptime(date_to, "%Y-%m-%d")
    except ValueError as exc:
        raise ValidationError("Даты периода должны быть в формате YYYY-MM-DD.") from exc
    if start > end:
        raise ValidationError("date_from не может быть позже date_to.")
    days = (end - start).days + 1
    if days > _MAX_PERIOD_DAYS:
        raise ValidationError(
            f"Период статистики не может превышать {_MAX_PERIOD_DAYS} дней, запрошено {days}."
        )


def campaign_statistics(
    account_id: int, campaign_id: int, date_from: str, date_to: str
) -> "Operation[CampaignStatisticResult]":
    _assert_period(date_from, date_to)
    return Operation(
        "POST",
        account_path(account_id, f"campaigns/{campaign_id}/stats"),
        {"dateFrom": date_from, "dateTo": date_to},
        lambda r: CampaignStatisticResult.from_dict(r.data),
    )


def group_statistics(
    account_id: int, campaign_id: int, date_from: str, date_to: str, group_ids: List[int]
) -> "Operation[List[GroupStatistic]]":
    _assert_period(date_from, date_to)
    return Operation(
        "POST",
        account_path(account_id, f"campaigns/{campaign_id}/groups/stats"),
        {"dateFrom": date_from, "dateTo": date_to, "groupIDs": list(group_ids)},
        lambda r: _entities(r.data.get("groups", []), GroupStatistic),
    )


def creative_statistics(
    account_id: int, campaign_id: int, date_from: str, date_to: str, creative_ids: List[int]
) -> "Operation[List[CreativeStatistic]]":
    _assert_period(date_from, date_to)
    return Operation(
        "POST",
        account_path(account_id, f"campaigns/{campaign_id}/creatives/stats"),
        {"dateFrom": date_from, "dateTo": date_to, "creativeIDs": list(creative_ids)},
        lambda r: _entities(r.data.get("creatives", []), CreativeStatistic),
    )


# --- Users ------------------------------------------------------------------


def list_users(account_id: int) -> "Operation[List[User]]":
    def parse(response: ApiResponse) -> List[User]:
        rows = response.data.get("users", []) or []
        return [User.from_dict(row) for row in rows if isinstance(row, dict)]

    return Operation("GET", account_path(account_id, "users"), None, parse)


def add_user(account_id: int, user_id: int, role: Union[str, UserRole]) -> "Operation[None]":
    role_value = UserRole.assert_valid(role)
    return Operation(
        "POST",
        account_path(account_id, "add-user"),
        {"userId": user_id, "role": role_value},
        lambda _r: None,
    )


def set_user_role(account_id: int, user_id: int, role: Union[str, UserRole]) -> "Operation[None]":
    role_value = UserRole.assert_valid(role)
    return Operation(
        "POST",
        account_path(account_id, "set-user-role"),
        {"userId": user_id, "role": role_value},
        lambda _r: None,
    )


def delete_user(account_id: int, user_id: int) -> "Operation[None]":
    return Operation(
        "DELETE", account_path(account_id, f"delete-user/{user_id}"), None, lambda _r: None
    )


DEFAULT_PAGE_LIMIT = DEFAULT_LIMIT
