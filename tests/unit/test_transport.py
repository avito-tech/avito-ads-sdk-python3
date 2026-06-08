"""Тесты транспортного слоя (sync + async): ошибки, повторы, токен, баланс лимита.

Каждый тест выполняется в двух режимах благодаря фикстурам ``mode``/``clients``.
"""

from __future__ import annotations

import pytest

from avito_ads.exceptions import (
    AccessDeniedError,
    AuthenticationError,
    BadRequestError,
    NotFoundError,
    RateLimitError,
    ServerError,
)

from ..conftest import ACCT_PATH, MockRouter, call

BALANCE = f"{ACCT_PATH}/balance"


async def test_success_parses_body_and_point_balance(clients):
    router = MockRouter()
    router.add_token()
    router.add("GET", BALANCE, json={"balance": 15000, "bonusBalance": 500},
               headers={"Api-Point-Balance": "4231"})
    client = clients(router)

    balance = await call(client.account.get_balance())
    assert balance.balance == 15000
    assert balance.bonus_balance == 500
    assert router.last.headers.get("Authorization") == "Bearer test-token"


@pytest.mark.parametrize(
    "status,exc",
    [
        (400, BadRequestError),
        (403, AccessDeniedError),
        (404, NotFoundError),
        (500, ServerError),
    ],
)
async def test_error_status_maps_to_exception(clients, status, exc):
    router = MockRouter()
    router.add_token()
    router.add("GET", BALANCE, json={"code": "e", "message": "Ошибка"}, status=status)
    client = clients(router)

    with pytest.raises(exc):
        await call(client.account.get_balance())


async def test_error_carries_code_and_message(clients):
    router = MockRouter()
    router.add_token()
    router.add("GET", BALANCE, json={"code": "bad_request", "message": "Плохой запрос"}, status=400)
    client = clients(router)

    with pytest.raises(BadRequestError) as info:
        await call(client.account.get_balance())
    assert info.value.error_code == "bad_request"
    assert info.value.status_code == 400
    assert str(info.value) == "Плохой запрос"


async def test_rate_limit_retry_after(clients):
    router = MockRouter()
    router.add_token()
    router.add("GET", BALANCE, json={"message": "too many"}, status=429,
               headers={"Retry-After": "7"})
    client = clients(router, max_retries=0)

    with pytest.raises(RateLimitError) as info:
        await call(client.account.get_balance())
    assert info.value.retry_after == 7


async def test_refreshes_token_and_retries_on_401(clients):
    router = MockRouter()
    router.add_token("tok-1")
    router.add("GET", BALANCE, json={"message": "expired"}, status=401)
    router.add_token("tok-2")
    router.add("GET", BALANCE, json={"balance": 777, "bonusBalance": 0})
    client = clients(router)

    balance = await call(client.account.get_balance())
    assert balance.balance == 777
    assert router.last.headers.get("Authorization") == "Bearer tok-2"


async def test_persistent_401_raises_authentication_error(clients):
    router = MockRouter()
    router.add_token("tok-1")
    router.add("GET", BALANCE, json={"message": "no"}, status=401)
    router.add_token("tok-2")
    router.add("GET", BALANCE, json={"message": "no"}, status=401)
    client = clients(router)

    with pytest.raises(AuthenticationError):
        await call(client.account.get_balance())


async def test_retries_on_429_then_succeeds(clients):
    router = MockRouter()
    router.add_token()
    router.add("GET", BALANCE, json={"message": "slow"}, status=429)
    router.add("GET", BALANCE, json={"balance": 10, "bonusBalance": 0})
    client = clients(router)

    balance = await call(client.account.get_balance())
    assert balance.balance == 10


async def test_retries_on_503_then_succeeds(clients):
    router = MockRouter()
    router.add_token()
    router.add("GET", BALANCE, json={"message": "down"}, status=503)
    router.add("GET", BALANCE, json={"balance": 11, "bonusBalance": 0})
    client = clients(router)

    balance = await call(client.account.get_balance())
    assert balance.balance == 11
