"""Асинхронный поставщик токена (OAuth2 client_credentials) на ``httpx.AsyncClient``."""

from __future__ import annotations

import logging
import time
from typing import Optional

import httpx

from .._version import build_user_agent
from ..auth.credentials import Credentials
from ..auth.storage import AsyncTokenStorage
from ..auth.token import AccessToken
from ..exceptions import AuthenticationError, NetworkError


class AsyncTokenProvider:
    """Асинхронное получение, кэширование и обновление токена через ``/token``."""

    def __init__(
        self,
        client: httpx.AsyncClient,
        credentials: Credentials,
        token_url: str,
        storage: AsyncTokenStorage,
        leeway: int = 60,
        timeout: float = 30.0,
        user_agent: Optional[str] = None,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        self._client = client
        self._credentials = credentials
        self._token_url = token_url
        self._storage = storage
        self._leeway = leeway
        self._timeout = timeout
        self._user_agent = build_user_agent(user_agent)
        self._logger = logger
        self._cache_key = credentials.cache_key()

    async def get_token(self) -> AccessToken:
        cached = await self._storage.get(self._cache_key)
        if cached is not None and not cached.is_expired(self._leeway):
            return cached
        token = await self._fetch_token()
        await self._storage.set(self._cache_key, token)
        return token

    async def forget_token(self) -> None:
        await self._storage.delete(self._cache_key)

    async def _fetch_token(self) -> AccessToken:
        if self._logger is not None:
            self._logger.debug("Запрос нового токена Авито Реклама (async).")
        try:
            response = await self._client.post(
                self._token_url,
                data={
                    "grant_type": "client_credentials",
                    "client_id": self._credentials.client_id,
                    "client_secret": self._credentials.client_secret,
                },
                headers={"Accept": "application/json", "User-Agent": self._user_agent},
                timeout=self._timeout,
            )
        except httpx.RequestError as exc:
            raise NetworkError(f"Не удалось получить токен: {exc}") from exc

        if response.status_code != 200:
            raise AuthenticationError(
                f"Не удалось получить токен (HTTP {response.status_code}).",
                status_code=response.status_code,
                response=response,
            )
        try:
            data = response.json()
        except ValueError as exc:
            raise AuthenticationError("Некорректный JSON в ответе эндпоинта /token.") from exc
        return AccessToken.from_response(data, now=time.time())
