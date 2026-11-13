"""Модели результатов операций создания."""

from __future__ import annotations

from typing import List, Optional

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
    """Результат создания тестового аккаунта (песочница).

    API отвечает ``200``, если аккаунт подготовлен полностью, и ``207``, если
    аккаунт создан, но часть sandbox-данных не подготовилась. Оба ответа —
    успех; причины во втором случае — в :attr:`warnings`.
    """

    @property
    def account_id(self) -> Optional[int]:
        return self._int("accountID")

    @property
    def warnings(self) -> List[str]:
        """Предупреждения о частично невыполненных sandbox-операциях.

        Пустой список — аккаунт подготовлен полностью.
        """
        return self._str_list("warnings")


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
