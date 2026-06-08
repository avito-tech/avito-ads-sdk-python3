"""Постраничная выборка и автоматический обход всех страниц."""

from __future__ import annotations

import os

from avito_ads import Client, Configuration


def main() -> None:
    client = Client(
        Configuration.create(
            os.environ["AVITO_ADS_CLIENT_ID"],
            os.environ["AVITO_ADS_CLIENT_SECRET"],
            int(os.environ["AVITO_ADS_ACCOUNT_ID"]),
        ).sandbox()
    )

    # Вариант 1: постранично вручную.
    page = client.campaigns.list(limit=50, page=1)
    print(f"Всего кампаний: {page.total}")
    print(f"Остаток лимита API: {page.api_point_balance}")
    for campaign in page:
        print(f"  - {campaign.id} {campaign.name}")

    # Вариант 2: обойти все страницы автоматически.
    count = sum(1 for _ in client.campaigns.iterate())
    print(f"Обойдено кампаний через iterate(): {count}")


if __name__ == "__main__":
    main()
