"""Быстрый старт (синхронный режим): реквизиты и баланс аккаунта.

Запуск:
    AVITO_ADS_CLIENT_ID=... AVITO_ADS_CLIENT_SECRET=... AVITO_ADS_ACCOUNT_ID=... \
    python examples/quickstart.py
"""

from __future__ import annotations

import os

from avito_ads import Client, Configuration
from avito_ads.exceptions import ApiError


def main() -> None:
    config = Configuration.create(
        os.environ["AVITO_ADS_CLIENT_ID"],
        os.environ["AVITO_ADS_CLIENT_SECRET"],
        int(os.environ["AVITO_ADS_ACCOUNT_ID"]),
    ).sandbox()  # для боевого окружения замените на .production()

    with Client(config) as client:
        try:
            account = client.account.get()
            print(f"Аккаунт: {account.short_name} (ИНН {account.inn})")

            balance = client.account.get_balance()
            print(f"Баланс: {balance.balance} ₽")
            print(f"Бонусы: {balance.bonus_balance}")

            for campaign in client.campaigns.iterate(limit=50):
                print(f"  кампания {campaign.id}: {campaign.name} [{campaign.status}]")
        except ApiError as exc:
            print(f"Ошибка API {exc.status_code}: {exc}")


if __name__ == "__main__":
    main()
