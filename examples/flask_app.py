"""Минимальный пример интеграции с Flask.

Запуск:
    pip install avito-ads[flask]
    AVITO_ADS_CLIENT_ID=... AVITO_ADS_CLIENT_SECRET=... AVITO_ADS_ACCOUNT_ID=... \
    flask --app examples/flask_app run
"""

from __future__ import annotations

import os

from flask import Flask

from avito_ads.integrations.flask import AvitoAds

app = Flask(__name__)
app.config.update(
    AVITO_ADS_CLIENT_ID=os.environ.get("AVITO_ADS_CLIENT_ID", ""),
    AVITO_ADS_CLIENT_SECRET=os.environ.get("AVITO_ADS_CLIENT_SECRET", ""),
    AVITO_ADS_ACCOUNT_ID=int(os.environ.get("AVITO_ADS_ACCOUNT_ID", "0")),
    AVITO_ADS_ENVIRONMENT=os.environ.get("AVITO_ADS_ENVIRONMENT", "sandbox"),
)

avito = AvitoAds(app)


@app.route("/balance")
def balance() -> dict:
    b = avito.client.account.get_balance()
    return {"balance": b.balance, "bonus": b.bonus_balance}
