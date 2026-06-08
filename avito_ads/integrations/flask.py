"""Интеграция с Flask.

Пример::

    from flask import Flask
    from avito_ads.integrations.flask import AvitoAds

    app = Flask(__name__)
    app.config.update(
        AVITO_ADS_CLIENT_ID="...",
        AVITO_ADS_CLIENT_SECRET="...",
        AVITO_ADS_ACCOUNT_ID=123456789,
        AVITO_ADS_ENVIRONMENT="production",
    )

    avito = AvitoAds(app)

    @app.route("/balance")
    def balance():
        return {"balance": avito.client.account.get_balance().balance}
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, Optional

from .. import Client
from ._common import build_configuration

if TYPE_CHECKING:  # pragma: no cover
    from flask import Flask

_CONFIG_KEYS = {
    "AVITO_ADS_CLIENT_ID": "client_id",
    "AVITO_ADS_CLIENT_SECRET": "client_secret",
    "AVITO_ADS_ACCOUNT_ID": "account_id",
    "AVITO_ADS_ENVIRONMENT": "environment",
    "AVITO_ADS_TIMEOUT": "timeout",
    "AVITO_ADS_MAX_RETRIES": "max_retries",
    "AVITO_ADS_RETRY_BASE_DELAY_MS": "retry_base_delay_ms",
    "AVITO_ADS_TOKEN_LEEWAY": "token_leeway",
}

_EXTENSION_NAME = "avito_ads"


class AvitoAds:
    """Расширение Flask, предоставляющее настроенный :class:`Client`."""

    def __init__(self, app: Optional["Flask"] = None) -> None:
        self._client: Optional[Client] = None
        if app is not None:
            self.init_app(app)

    def init_app(self, app: "Flask") -> None:
        """Инициализирует расширение из ``app.config``."""
        settings: Dict[str, Any] = {}
        for flask_key, setting_key in _CONFIG_KEYS.items():
            if flask_key in app.config and app.config[flask_key] is not None:
                settings[setting_key] = app.config[flask_key]

        config = build_configuration(settings)
        self._client = Client(config)

        if not hasattr(app, "extensions"):  # pragma: no cover
            app.extensions = {}
        app.extensions[_EXTENSION_NAME] = self

    @property
    def client(self) -> Client:
        """Готовый клиент Авито Реклама."""
        if self._client is None:
            raise RuntimeError(
                "Расширение AvitoAds не инициализировано. Вызовите init_app(app)."
            )
        return self._client
