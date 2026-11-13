"""Иерархия исключений SDK Авито Реклама.

Все исключения наследуются от :class:`AvitoAdsError`, что позволяет перехватывать
любую ошибку библиотеки одним ``except``. Ошибки HTTP-уровня наследуются от
:class:`ApiError` и несут код состояния, код ошибки API и (при наличии) объекты
запроса/ответа транспорта (``httpx.Request`` / ``httpx.Response``).

Эти классы общие для синхронного и асинхронного режимов.
"""

from __future__ import annotations

from typing import Any, Optional


class AvitoAdsError(Exception):
    """Базовое исключение для всех ошибок SDK."""


class ConfigurationError(AvitoAdsError, ValueError):
    """Некорректная конфигурация клиента."""


class ValidationError(AvitoAdsError, ValueError):
    """Ошибка валидации входных данных на стороне клиента (до запроса к API)."""


class ApiError(AvitoAdsError):
    """Базовая ошибка ответа API.

    :param message: человекочитаемое сообщение об ошибке.
    :param status_code: HTTP-код ответа.
    :param error_code: код ошибки из тела ответа (поле ``code``), если есть.
    :param request: объект запроса (``httpx.Request``), если доступен.
    :param response: объект ответа (``httpx.Response``), если доступен.
    """

    def __init__(
        self,
        message: str,
        status_code: int = 0,
        error_code: Optional[str] = None,
        request: Optional[Any] = None,
        response: Optional[Any] = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.error_code = error_code
        self.request = request
        self.response = response


class BadRequestError(ApiError):
    """HTTP 400 — некорректный запрос."""


class AuthenticationError(ApiError):
    """HTTP 401 — ошибка аутентификации (невалидный или просроченный токен)."""


class AccessDeniedError(ApiError):
    """HTTP 403 — доступ запрещён."""


class NotFoundError(ApiError):
    """HTTP 404 — ресурс не найден."""


class ConflictError(ApiError):
    """HTTP 409 — конфликт версий.

    API возвращает 409 в ``change-budget`` и ``change-price``, если группу
    изменили параллельно. Наследник :class:`ApiError`: обработчики по базовому
    классу продолжают ловить эту ошибку. Обычно достаточно перечитать группу и
    повторить изменение.
    """


class RateLimitError(ApiError):
    """HTTP 429 — превышен лимит запросов.

    :param retry_after: значение заголовка ``Retry-After`` в секундах, если есть.
    """

    def __init__(
        self,
        message: str,
        status_code: int = 429,
        error_code: Optional[str] = None,
        request: Optional[Any] = None,
        response: Optional[Any] = None,
        retry_after: Optional[int] = None,
    ) -> None:
        super().__init__(message, status_code, error_code, request, response)
        self.retry_after = retry_after


class ServerError(ApiError):
    """HTTP 5xx — ошибка на стороне сервера."""


class NetworkError(ApiError):
    """Сетевая ошибка или таймаут соединения."""
