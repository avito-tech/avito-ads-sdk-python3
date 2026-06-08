"""Модель пользователя аккаунта."""

from __future__ import annotations

from typing import Optional

from .base import Model


class User(Model):
    """Пользователь аккаунта."""

    @property
    def id(self) -> Optional[int]:
        return self._int("id")

    @property
    def role(self) -> Optional[str]:
        return self._str("role")

    @property
    def has_logged_in(self) -> Optional[bool]:
        return self._bool("hasLoggedIn")
