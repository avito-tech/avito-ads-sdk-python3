"""Тесты поставщика токена (sync + async) через httpx.MockTransport."""

from __future__ import annotations

import httpx
import pytest

from avito_ads._async.token_provider import AsyncTokenProvider
from avito_ads._sync.token_provider import SyncTokenProvider
from avito_ads.auth.credentials import Credentials
from avito_ads.auth.storage import InMemoryAsyncTokenStorage, InMemoryTokenStorage
from avito_ads.exceptions import AuthenticationError

from ..conftest import TOKEN_PATH, MockRouter, call

TOKEN_URL = "https://api.avito.ru/token"


def _make_provider(mode: str, router: MockRouter):
    """Создаёт поставщик токена нужного режима поверх мок-транспорта."""
    transport = httpx.MockTransport(router.handler)
    creds = Credentials("cid", "secret")
    if mode == "async":
        client = httpx.AsyncClient(transport=transport)
        return AsyncTokenProvider(client, creds, TOKEN_URL, InMemoryAsyncTokenStorage())
    client = httpx.Client(transport=transport)
    return SyncTokenProvider(client, creds, TOKEN_URL, InMemoryTokenStorage())


async def test_fetches_and_caches_token(mode):
    router = MockRouter()
    router.add_token("tok-1")
    provider = _make_provider(mode, router)

    first = await call(provider.get_token())
    second = await call(provider.get_token())
    assert first.token == "tok-1"
    assert second.token == "tok-1"
    # Второй вызов берёт из кэша — был лишь один POST /token.
    token_calls = [r for r in router.requests if r.url.path == TOKEN_PATH]
    assert len(token_calls) == 1


async def test_forget_token_forces_refetch(mode):
    router = MockRouter()
    router.add_token("tok-1")
    router.add_token("tok-2")
    provider = _make_provider(mode, router)

    assert (await call(provider.get_token())).token == "tok-1"
    await call(provider.forget_token())
    assert (await call(provider.get_token())).token == "tok-2"


async def test_expired_token_is_refetched(mode):
    router = MockRouter()
    # expires_in=1 при leeway=60 → токен сразу считается истёкшим.
    router.add_token("tok-1", expires_in=1)
    router.add_token("tok-2")
    provider = _make_provider(mode, router)

    assert (await call(provider.get_token())).token == "tok-1"
    assert (await call(provider.get_token())).token == "tok-2"


async def test_invalid_token_response_raises(mode):
    router = MockRouter()
    router.add("POST", TOKEN_PATH, json={"foo": "bar"})
    provider = _make_provider(mode, router)

    with pytest.raises(AuthenticationError):
        await call(provider.get_token())


async def test_http_error_on_token_raises(mode):
    router = MockRouter()
    router.add("POST", TOKEN_PATH, text="nope", status=401)
    provider = _make_provider(mode, router)

    with pytest.raises(AuthenticationError):
        await call(provider.get_token())
