"""Модель группы объявлений."""

from __future__ import annotations

from typing import Optional

from .base import Model


class Group(Model):
    """Группа объявлений."""

    @property
    def id(self) -> Optional[int]:
        return self._int("id")

    @property
    def name(self) -> Optional[str]:
        return self._str("name")

    @property
    def account_id(self) -> Optional[int]:
        return self._int("accountID")

    @property
    def campaign_id(self) -> Optional[int]:
        return self._int("campaignID")

    @property
    def status(self) -> Optional[str]:
        return self._str("status")

    @property
    def budget(self) -> Optional[int]:
        return self._int("budget")

    @property
    def price(self) -> Optional[int]:
        return self._int("price")

    @property
    def payment_model(self) -> Optional[str]:
        return self._str("paymentModel")

    @property
    def campaign_type(self) -> Optional[str]:
        return self._str("campaignType")

    @property
    def advertiser_id(self) -> Optional[int]:
        return self._int("advertiserID")

    @property
    def manager_id(self) -> Optional[int]:
        return self._int("managerID")

    @property
    def have_creative(self) -> Optional[bool]:
        return self._bool("haveCreative")

    @property
    def created_at(self) -> Optional[str]:
        return self._str("createdAt")

    @property
    def updated_at(self) -> Optional[str]:
        return self._str("updatedAt")
