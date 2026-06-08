"""Быстрый старт (асинхронный режим): реквизиты, баланс и перебор кампаний.

Запуск:
    AVITO_ADS_CLIENT_ID=... AVITO_ADS_CLIENT_SECRET=... AVITO_ADS_ACCOUNT_ID=... \
    python examples/async_quickstart.py
"""

from __future__ import annotations

import asyncio
import os

from avito_ads import AsyncClient, Configuration
from avito_ads.exceptions import ApiError


async def main() -> None:
    config = Configuration.create(
        os.environ["AVITO_ADS_CLIENT_ID"],
        os.environ["AVITO_ADS_CLIENT_SECRET"],
        int(os.environ["AVITO_ADS_ACCOUNT_ID"]),
    ).sandbox()  # для боевого окружения замените на .production()

    async with AsyncClient(config) as client:
        try:
            account = await client.account.get()
            print(f"Аккаунт: {account.short_name} (ИНН {account.inn})")

            balance = await client.account.get_balance()
            print(f"Баланс: {balance.balance} ₽, бонусы: {balance.bonus_balance}")

            # Параллельный запрос нескольких ресурсов.
            campaigns_page, users = await asyncio.gather(
                client.campaigns.list(limit=10),
                client.users.list(),
            )
            print(f"Кампаний всего: {campaigns_page.total}; пользователей: {len(users)}")

            # Асинхронный перебор всех страниц.
            async for campaign in client.campaigns.iterate(limit=50):
                print(f"  кампания {campaign.id}: {campaign.name} [{campaign.status}]")
        except ApiError as exc:
            print(f"Ошибка API {exc.status_code}: {exc}")


if __name__ == "__main__":
    asyncio.run(main())
