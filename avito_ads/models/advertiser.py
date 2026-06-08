"""Модель рекламодателя."""

from __future__ import annotations

from typing import Optional

from .base import Model


class Advertiser(Model):
    """Рекламодатель."""

    @property
    def id(self) -> Optional[int]:
        return self._int("id")

    @property
    def short_name(self) -> Optional[str]:
        return self._str("shortName")

    @property
    def long_name(self) -> Optional[str]:
        return self._str("longName")

    @property
    def inn(self) -> Optional[str]:
        return self._str("inn")

    @property
    def ogrn(self) -> Optional[str]:
        return self._str("ogrn")

    @property
    def kpp(self) -> Optional[str]:
        return self._str("kpp")

    @property
    def legal_address(self) -> Optional[str]:
        return self._str("legalAddress")

    @property
    def actual_address(self) -> Optional[str]:
        return self._str("actualAddress")

    @property
    def legal_type(self) -> Optional[str]:
        return self._str("legalType")

    @property
    def legal_role(self) -> Optional[str]:
        return self._str("legalRole")

    @property
    def account_id(self) -> Optional[int]:
        return self._int("accountId")
