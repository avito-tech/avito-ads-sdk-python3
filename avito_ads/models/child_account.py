"""Модель дочернего аккаунта."""

from __future__ import annotations

from typing import Any, Dict, Optional

from .account import Balance
from .base import Model


class ChildAccount(Model):
    """Дочерний аккаунт (данные аккаунта вложены в ключ ``account``)."""

    @property
    def id(self) -> Optional[int]:
        account = self._dict("account")
        value = account.get("id")
        return int(value) if value is not None else None

    @property
    def short_name(self) -> Optional[str]:
        account = self._dict("account")
        value = account.get("shortName")
        return str(value) if value is not None else None

    @property
    def contract(self) -> Dict[str, Any]:
        return self._dict("contract")

    @property
    def balance(self) -> Optional[Balance]:
        data = self._dict("balance")
        return Balance.from_dict(data) if data else None
