"""Статистика по кампании за период (не более 100 дней)."""

from __future__ import annotations

import os

from avito_ads import Client, Configuration
from avito_ads.exceptions import ValidationError


def main() -> None:
    client = Client(
        Configuration.create(
            os.environ["AVITO_ADS_CLIENT_ID"],
            os.environ["AVITO_ADS_CLIENT_SECRET"],
            int(os.environ["AVITO_ADS_ACCOUNT_ID"]),
        ).sandbox()
    )

    campaign_id = int(os.environ.get("AVITO_ADS_CAMPAIGN_ID", "0"))

    try:
        stats = client.statistics.campaign(campaign_id, "2025-01-01", "2025-01-31")
        total = stats.campaign.total_data
        print(f"Показы: {total.views}")
        print(f"Клики: {total.clicks}")
        print(f"Расход: {total.spend} ₽")
    except ValidationError as exc:
        print(f"Ошибка валидации: {exc}")


if __name__ == "__main__":
    main()
