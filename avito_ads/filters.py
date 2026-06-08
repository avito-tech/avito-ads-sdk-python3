"""Фильтры для постраничных запросов.

Каждый фильтр — это билдер с цепочкой методов; ``to_dict`` возвращает словарь
с теми именами полей, которые ожидает API (например, ``contractIDs``). Фильтры
можно не использовать и передавать обычный словарь напрямую.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass(frozen=True)
class DateRange:
    """Диапазон дат в формате ``YYYY-MM-DD``."""

    from_date: str
    to_date: str

    def to_dict(self) -> Dict[str, str]:
        return {"from": self.from_date, "to": self.to_date}


class BaseFilter:
    """Базовый билдер фильтра, накапливающий пары ключ-значение."""

    def __init__(self) -> None:
        self._data: Dict[str, Any] = {}

    def _set(self, key: str, value: Any) -> "BaseFilter":
        self._data[key] = value
        return self

    def to_dict(self) -> Dict[str, Any]:
        """Возвращает словарь фильтра с именами полей API."""
        return dict(self._data)


class AdvertiserFilter(BaseFilter):
    """Фильтр рекламодателей."""

    def ids(self, ids: List[int]) -> "AdvertiserFilter":
        self._set("ids", ids)
        return self

    def inns(self, inns: List[str]) -> "AdvertiserFilter":
        self._set("inns", inns)
        return self

    def roles(self, roles: List[str]) -> "AdvertiserFilter":
        self._set("roles", roles)
        return self


class ContractsFilter(BaseFilter):
    """Фильтр договоров."""

    def ids(self, ids: List[int]) -> "ContractsFilter":
        self._set("ids", ids)
        return self

    def numbers(self, numbers: List[str]) -> "ContractsFilter":
        self._set("numbers", numbers)
        return self

    def contractors(self, contractors: List[int]) -> "ContractsFilter":
        self._set("contractors", contractors)
        return self

    def clients(self, clients: List[int]) -> "ContractsFilter":
        self._set("clients", clients)
        return self


class CampaignsFilter(BaseFilter):
    """Фильтр кампаний."""

    def ids(self, ids: List[int]) -> "CampaignsFilter":
        self._set("ids", ids)
        return self

    def payment_models(self, models: List[str]) -> "CampaignsFilter":
        self._set("paymentModels", models)
        return self

    def campaign_types(self, types: List[str]) -> "CampaignsFilter":
        self._set("campaignTypes", types)
        return self

    def statuses(self, statuses: List[str]) -> "CampaignsFilter":
        self._set("statuses", statuses)
        return self

    def managers(self, managers: List[int]) -> "CampaignsFilter":
        self._set("managers", managers)
        return self

    def advertisers(self, advertisers: List[int]) -> "CampaignsFilter":
        self._set("advertisers", advertisers)
        return self

    def contract_ids(self, ids: List[int]) -> "CampaignsFilter":
        self._set("contractIDs", ids)
        return self

    def additional_agreement_ids(self, ids: List[int]) -> "CampaignsFilter":
        self._set("additionalAgreementIDs", ids)
        return self

    def created_at(self, date_range: DateRange) -> "CampaignsFilter":
        self._set("createdAt", date_range.to_dict())
        return self

    def time_frame(self, date_range: DateRange) -> "CampaignsFilter":
        self._set("timeFrame", date_range.to_dict())
        return self


class GroupsFilter(BaseFilter):
    """Фильтр групп объявлений."""

    def ids(self, ids: List[int]) -> "GroupsFilter":
        self._set("ids", ids)
        return self

    def campaign_ids(self, ids: List[int]) -> "GroupsFilter":
        self._set("campaignIDs", ids)
        return self

    def statuses(self, statuses: List[str]) -> "GroupsFilter":
        self._set("statuses", statuses)
        return self

    def paces(self, paces: List[str]) -> "GroupsFilter":
        self._set("paces", paces)
        return self

    def managers(self, managers: List[int]) -> "GroupsFilter":
        self._set("managers", managers)
        return self

    def advertisers(self, advertisers: List[int]) -> "GroupsFilter":
        self._set("advertisers", advertisers)
        return self

    def payment_models(self, models: List[str]) -> "GroupsFilter":
        self._set("paymentModels", models)
        return self

    def time_frame(self, date_range: DateRange) -> "GroupsFilter":
        self._set("timeFrame", date_range.to_dict())
        return self


class CreativesFilter(BaseFilter):
    """Фильтр креативов."""

    def ids(self, ids: List[int]) -> "CreativesFilter":
        self._set("ids", ids)
        return self

    def group_ids(self, ids: List[int]) -> "CreativesFilter":
        self._set("groupIDs", ids)
        return self

    def campaign_ids(self, ids: List[int]) -> "CreativesFilter":
        self._set("campaignIDs", ids)
        return self

    def payment_models(self, models: List[str]) -> "CreativesFilter":
        self._set("paymentModels", models)
        return self

    def campaign_types(self, types: List[str]) -> "CreativesFilter":
        self._set("campaignTypes", types)
        return self

    def statuses(self, statuses: List[str]) -> "CreativesFilter":
        self._set("statuses", statuses)
        return self

    def managers(self, managers: List[int]) -> "CreativesFilter":
        self._set("managers", managers)
        return self

    def advertisers(self, advertisers: List[int]) -> "CreativesFilter":
        self._set("advertisers", advertisers)
        return self

    def time_frame(self, date_range: DateRange) -> "CreativesFilter":
        self._set("timeFrame", date_range.to_dict())
        return self
