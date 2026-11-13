"""Тесты заголовка User-Agent (sync + async): метка SDK, дописывание, запрос токена."""

from __future__ import annotations

import httpx

import avito_ads
from avito_ads import AsyncClient, Client, Configuration
from avito_ads._version import build_user_agent

from ..conftest import ACCOUNT_ID, ACCT_PATH, TOKEN_PATH, MockRouter, aclose, call

BALANCE = f"{ACCT_PATH}/balance"
SDK_MARK = f"avito-ads-sdk-python3/{avito_ads.__version__}"


def _client(mode: str, router: MockRouter, user_agent: str = "") -> object:
    config = Configuration.create("id", "secret", ACCOUNT_ID).with_retry_base_delay(0)
    if user_agent:
        config = config.with_user_agent(user_agent)
    transport = httpx.MockTransport(router.handler)
    if mode == "async":
        return AsyncClient(config.with_async_client(httpx.AsyncClient(transport=transport)))
    return Client(config.with_http_client(httpx.Client(transport=transport)))


async def _user_agents(mode: str, user_agent: str = "") -> dict:
    router = MockRouter()
    router.add_token()
    router.add("GET", BALANCE, json={"balance": 1, "bonusBalance": 0})
    client = _client(mode, router, user_agent)
    try:
        await call(client.account.get_balance())  # type: ignore[attr-defined]
    finally:
        await aclose(client)
    return {req.url.path: req.headers.get("User-Agent") for req in router.requests}


def test_default_user_agent_constant():
    assert avito_ads.DEFAULT_USER_AGENT == SDK_MARK
    assert Configuration.create("id", "secret", 1).effective_user_agent == SDK_MARK


async def test_default_user_agent_in_requests_and_token(mode):
    agents = await _user_agents(mode)
    assert agents[BALANCE] == SDK_MARK
    assert agents[TOKEN_PATH] == SDK_MARK


async def test_custom_user_agent_gets_sdk_mark(mode):
    agents = await _user_agents(mode, "my-app/1.0")
    assert agents[BALANCE] == f"my-app/1.0 {SDK_MARK}"
    assert agents[TOKEN_PATH] == f"my-app/1.0 {SDK_MARK}"


async def test_custom_user_agent_with_mark_is_not_duplicated(mode):
    custom = "my-app/1.0 Avito-Ads-SDK-Python3/9.9.9"
    agents = await _user_agents(mode, custom)
    assert agents[BALANCE] == custom
    assert agents[TOKEN_PATH] == custom


def test_build_user_agent_edge_cases():
    assert build_user_agent(None) == SDK_MARK
    assert build_user_agent("   ") == SDK_MARK
    assert build_user_agent(" my-app/1.0 ") == f"my-app/1.0 {SDK_MARK}"
    assert build_user_agent(SDK_MARK) == SDK_MARK
