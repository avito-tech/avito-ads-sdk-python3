"""Модели аккаунта и баланса."""

from __future__ import annotations

from typing import Any, Dict, Optional

from .base import Model


class Account(Model):
    """Реквизиты рекламного аккаунта."""

    @property
    def inn(self) -> Optional[str]:
        return self._str("inn")

    @property
    def short_name(self) -> Optional[str]:
        return self._str("shortName")

    @property
    def long_name(self) -> Optional[str]:
        return self._str("longName")

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
    def contact(self) -> Dict[str, Any]:
        return self._dict("contact")

    @property
    def manager(self) -> Dict[str, Any]:
        return self._dict("manager")


class Balance(Model):
    """Баланс аккаунта: целые рубли и точные суммы в копейках."""

    @property
    def balance(self) -> int:
        """Баланс в рублях."""
        return self._int("balance") or 0

    @property
    def bonus_balance(self) -> int:
        """Бонусный баланс в рублях."""
        return self._int("bonusBalance") or 0

    @property
    def balance_kopeks(self) -> int:
        """Баланс в копейках (``balanceKopeks``)."""
        return self._int("balanceKopeks") or 0

    @property
    def bonus_balance_kopeks(self) -> int:
        """Бонусный баланс в копейках (``bonusBalanceKopeks``)."""
        return self._int("bonusBalanceKopeks") or 0
