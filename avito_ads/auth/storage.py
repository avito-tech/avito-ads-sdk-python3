"""Хранилища токена доступа.

По умолчанию используется хранилище в памяти процесса. Для переиспользования
токена между запусками реализуйте :class:`TokenStorage` (например, поверх Redis
или файловой системы) и передайте его в конфигурацию через ``with_token_storage``.
"""

from __future__ import annotations

# ``Protocol`` и ``runtime_checkable`` есть в ``typing`` начиная с Python 3.8 —
# минимальной поддерживаемой версии, поэтому запасной импорт не нужен.
from typing import Dict, Optional, Protocol, runtime_checkable

from .token import AccessToken


@runtime_checkable
class TokenStorage(Protocol):
    """Интерфейс хранилища токена."""

    def get(self, key: str) -> Optional[AccessToken]:
        """Возвращает токен по ключу или ``None``, если его нет."""
        ...

    def set(self, key: str, token: AccessToken) -> None:
        """Сохраняет токен по ключу."""
        ...

    def delete(self, key: str) -> None:
        """Удаляет токен по ключу."""
        ...


class InMemoryTokenStorage:
    """Хранилище токена в памяти процесса (по умолчанию)."""

    def __init__(self) -> None:
        self._store: Dict[str, AccessToken] = {}

    def get(self, key: str) -> Optional[AccessToken]:
        return self._store.get(key)

    def set(self, key: str, token: AccessToken) -> None:
        self._store[key] = token

    def delete(self, key: str) -> None:
        self._store.pop(key, None)


@runtime_checkable
class AsyncTokenStorage(Protocol):
    """Интерфейс асинхронного хранилища токена.

    Используется асинхронным клиентом. Реализуйте поверх асинхронного Redis и
    передайте через ``Configuration.with_async_token_storage``.
    """

    async def get(self, key: str) -> Optional[AccessToken]:
        """Возвращает токен по ключу или ``None``, если его нет."""
        ...

    async def set(self, key: str, token: AccessToken) -> None:
        """Сохраняет токен по ключу."""
        ...

    async def delete(self, key: str) -> None:
        """Удаляет токен по ключу."""
        ...


class InMemoryAsyncTokenStorage:
    """Асинхронное хранилище токена в памяти процесса (по умолчанию для async)."""

    def __init__(self) -> None:
        self._store: Dict[str, AccessToken] = {}

    async def get(self, key: str) -> Optional[AccessToken]:
        return self._store.get(key)

    async def set(self, key: str, token: AccessToken) -> None:
        self._store[key] = token

    async def delete(self, key: str) -> None:
        self._store.pop(key, None)
