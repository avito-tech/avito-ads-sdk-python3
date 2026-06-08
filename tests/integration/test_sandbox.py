"""Интеграционные тесты против реальной песочницы Авито Реклама (sync + async).

По умолчанию пропускаются. Чтобы запустить, задайте переменные окружения и флаг::

    AVITO_ADS_RUN_INTEGRATION=1 \
    AVITO_ADS_CLIENT_ID=... \
    AVITO_ADS_CLIENT_SECRET=... \
    AVITO_ADS_ACCOUNT_ID=... \
    pytest -m integration

Тесты выполняют только безопасные операции чтения.
"""

from __future__ import annotations

import os

import pytest

from avito_ads import AsyncClient, Client, Configuration

pytestmark = pytest.mark.integration

_ENABLED = os.getenv("AVITO_ADS_RUN_INTEGRATION") == "1"
_CREDS = all(
    os.getenv(name)
    for name in ("AVITO_ADS_CLIENT_ID", "AVITO_ADS_CLIENT_SECRET", "AVITO_ADS_ACCOUNT_ID")
)

skip_reason = "Интеграционные тесты отключены (нет AVITO_ADS_RUN_INTEGRATION или учётных данных)."


def _config() -> Configuration:
    return Configuration.create(
        os.environ["AVITO_ADS_CLIENT_ID"],
        os.environ["AVITO_ADS_CLIENT_SECRET"],
        int(os.environ["AVITO_ADS_ACCOUNT_ID"]),
    ).sandbox()


@pytest.mark.skipif(not (_ENABLED and _CREDS), reason=skip_reason)
def test_sync_can_read_balance():
    with Client(_config()) as client:
        balance = client.account.get_balance()
        assert isinstance(balance.balance, int)
        assert isinstance(balance.bonus_balance, int)


@pytest.mark.skipif(not (_ENABLED and _CREDS), reason=skip_reason)
def test_sync_can_list_campaigns():
    with Client(_config()) as client:
        result = client.campaigns.list()
        assert result.total >= 0


@pytest.mark.skipif(not (_ENABLED and _CREDS), reason=skip_reason)
async def test_async_can_read_balance():
    async with AsyncClient(_config()) as client:
        balance = await client.account.get_balance()
        assert isinstance(balance.balance, int)


@pytest.mark.skipif(not (_ENABLED and _CREDS), reason=skip_reason)
async def test_async_can_iterate_campaigns():
    async with AsyncClient(_config()) as client:
        count = 0
        async for _campaign in client.campaigns.iterate():
            count += 1
            if count >= 5:
                break
        assert count >= 0
