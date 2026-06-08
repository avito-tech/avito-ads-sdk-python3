"""Интеграция с Django.

Настройте в ``settings.py``::

    AVITO_ADS = {
        "client_id": "...",
        "client_secret": "...",
        "account_id": 123456789,
        "environment": "production",
    }

И используйте готовый клиент::

    from avito_ads.integrations.django import get_client

    balance = get_client().account.get_balance()

Опционально можно подключить приложение, добавив
``"avito_ads.integrations.django"`` в ``INSTALLED_APPS`` — это включит проверку
конфигурации при старте через ``AppConfig.ready``.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from .. import Client
from ..exceptions import ConfigurationError
from ._common import build_configuration

try:  # pragma: no cover - доступно только при установленном Django
    from django.apps import AppConfig as _DjangoAppConfig
    from django.conf import settings as _django_settings

    _DJANGO_AVAILABLE = True
except ImportError:  # pragma: no cover
    _DJANGO_AVAILABLE = False
    _DjangoAppConfig = object

_client: Optional[Client] = None


def _read_settings() -> Dict[str, Any]:
    if not _DJANGO_AVAILABLE:  # pragma: no cover
        raise ConfigurationError("Django не установлен.")
    raw = getattr(_django_settings, "AVITO_ADS", None)
    if not isinstance(raw, dict):
        raise ConfigurationError(
            "Не найдена настройка AVITO_ADS (словарь) в settings Django."
        )
    return dict(raw)


def build_client() -> Client:
    """Создаёт новый клиент из настроек Django (без кэширования)."""
    return Client(build_configuration(_read_settings()))


def get_client() -> Client:
    """Возвращает клиент-синглтон, создавая его при первом обращении."""
    global _client
    if _client is None:
        _client = build_client()
    return _client


if _DJANGO_AVAILABLE:  # pragma: no cover

    class AvitoAdsConfig(_DjangoAppConfig):  # type: ignore[misc]
        """AppConfig приложения интеграции."""

        name = "avito_ads.integrations.django"
        label = "avito_ads"
        verbose_name = "Avito Ads"

        def ready(self) -> None:
            # Ранняя валидация конфигурации при старте приложения.
            _read_settings()
