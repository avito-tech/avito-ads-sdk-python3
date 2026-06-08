"""Модели результатов операций создания."""

from __future__ import annotations

from typing import Optional

from .base import Model


class CreatedContract(Model):
    """Результат создания договора."""

    @property
    def id(self) -> Optional[int]:
        return self._int("id")


class CreatedAdvertiser(Model):
    """Результат создания рекламодателя."""

    @property
    def id(self) -> Optional[int]:
        return self._int("id")


class CreatedAccount(Model):
    """Результат создания тестового аккаунта (песочница)."""

    @property
    def account_id(self) -> Optional[int]:
        return self._int("accountID")


class CreatedChildAccount(Model):
    """Результат создания дочернего аккаунта."""

    @property
    def account_id(self) -> Optional[int]:
        return self._int("accountID")

    @property
    def client_key(self) -> Optional[str]:
        return self._str("clientKey")

    @property
    def client_secret(self) -> Optional[str]:
        return self._str("clientSecret")
