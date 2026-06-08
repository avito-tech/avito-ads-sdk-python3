"""Общий помощник: сборка :class:`Configuration` из словаря настроек."""

from __future__ import annotations

from typing import Any, Mapping, Optional

from ..auth.storage import TokenStorage
from ..configuration import Configuration


def build_configuration(
    settings: Mapping[str, Any],
    token_storage: Optional[TokenStorage] = None,
) -> Configuration:
    """Собирает конфигурацию из словаря настроек.

    Ожидаемые ключи: ``client_id``, ``client_secret``, ``account_id``,
    ``environment`` (``production``/``sandbox``), а также необязательные
    ``timeout``, ``max_retries``, ``retry_base_delay_ms``, ``token_leeway``.
    """
    config = Configuration.create(
        str(settings.get("client_id", "")),
        str(settings.get("client_secret", "")),
        int(settings.get("account_id", 0)),
    )

    config = (
        config.sandbox()
        if settings.get("environment", "production") == "sandbox"
        else config.production()
    )

    if "timeout" in settings:
        config = config.with_timeout(float(settings["timeout"]))
    if "max_retries" in settings:
        config = config.with_max_retries(int(settings["max_retries"]))
    if "retry_base_delay_ms" in settings:
        config = config.with_retry_base_delay(int(settings["retry_base_delay_ms"]))
    if "token_leeway" in settings:
        config = config.with_token_leeway(int(settings["token_leeway"]))
    if token_storage is not None:
        config = config.with_token_storage(token_storage)

    return config
