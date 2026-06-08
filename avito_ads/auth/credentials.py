"""Учётные данные приложения для OAuth2 client_credentials."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass


@dataclass(frozen=True)
class Credentials:
    """Идентификатор и секрет приложения Авито Реклама.

    :param client_id: идентификатор приложения (client_id).
    :param client_secret: секрет приложения (client_secret).
    """

    client_id: str
    client_secret: str

    def cache_key(self) -> str:
        """Стабильный ключ кэширования токена, не раскрывающий секрет."""
        digest = hashlib.sha1(f"{self.client_id}:{self.client_secret}".encode()).hexdigest()
        return f"avito_ads_token_{digest}"
