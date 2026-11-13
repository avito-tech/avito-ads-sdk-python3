"""Транспортно-независимая («sans-I/O») логика HTTP-слоя.

Здесь нет ни одного сетевого вызова — только чистые функции, которые одинаково
используются синхронным и асинхронным транспортом. Это гарантирует, что правила
повторов, разбор ответа и отображение ошибок не разойдутся между режимами.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional

from ..exceptions import (
    AccessDeniedError,
    ApiError,
    AuthenticationError,
    BadRequestError,
    ConflictError,
    NotFoundError,
    RateLimitError,
    ServerError,
)
from .response import ApiResponse

# Тип функции доступа к заголовку (``response.headers.get`` у httpx).
HeaderGetter = Callable[[str], Optional[str]]


def build_headers(authorization: str, has_body: bool) -> Dict[str, str]:
    """Формирует заголовки запроса."""
    headers = {
        "Authorization": authorization,
        "Accept": "application/json",
    }
    if has_body:
        headers["Content-Type"] = "application/json"
    return headers


def retry_after_seconds(header_get: HeaderGetter) -> Optional[int]:
    """Извлекает ``Retry-After`` (секунды) из заголовков или ``None``."""
    value = header_get("Retry-After")
    if value is None:
        return None
    try:
        seconds = int(value)
    except (TypeError, ValueError):
        return None
    return seconds if seconds >= 0 else None


def point_balance(header_get: HeaderGetter) -> Optional[int]:
    """Извлекает остаток лимита из заголовка ``Api-Point-Balance``."""
    value = header_get("Api-Point-Balance")
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def parse_body(content: bytes, json_loader: Callable[[], Any]) -> Dict[str, Any]:
    """Разбирает тело ответа в словарь.

    :param content: сырые байты тела (для проверки на пустоту).
    :param json_loader: функция разбора JSON (``response.json``).
    """
    if not content:
        return {}
    try:
        parsed = json_loader()
    except ValueError:
        return {}
    if isinstance(parsed, dict):
        return parsed
    return {"data": parsed}


def make_api_response(
    status_code: int,
    header_get: HeaderGetter,
    content: bytes,
    json_loader: Callable[[], Any],
) -> ApiResponse:
    """Собирает :class:`ApiResponse` из частей ответа транспорта."""
    return ApiResponse(
        status_code=status_code,
        data=parse_body(content, json_loader),
        api_point_balance=point_balance(header_get),
    )


def error_from_response(
    status_code: int,
    data: Dict[str, Any],
    header_get: HeaderGetter,
    request: Optional[Any] = None,
    response: Optional[Any] = None,
) -> ApiError:
    """Отображает код состояния и тело ответа на типизированное исключение."""
    message = str(data.get("message") or f"Ошибка API (HTTP {status_code}).")
    raw_code = data.get("code")
    error_code = str(raw_code) if raw_code is not None else None

    if status_code == 400:
        return BadRequestError(message, status_code, error_code, request, response)
    if status_code == 401:
        return AuthenticationError(message, status_code, error_code, request, response)
    if status_code == 403:
        return AccessDeniedError(message, status_code, error_code, request, response)
    if status_code == 404:
        return NotFoundError(message, status_code, error_code, request, response)
    if status_code == 409:
        return ConflictError(message, status_code, error_code, request, response)
    if status_code == 429:
        return RateLimitError(
            message,
            status_code,
            error_code,
            request,
            response,
            retry_after_seconds(header_get),
        )
    if status_code >= 500:
        return ServerError(message, status_code, error_code, request, response)
    return ApiError(message, status_code, error_code, request, response)


# --- Политика повторов ------------------------------------------------------

RETURN = "return"
RAISE = "raise"
REFRESH = "refresh"
WAIT = "wait"


@dataclass(frozen=True)
class RetryPlan:
    """Решение о следующем шаге после получения ответа.

    :param action: одно из ``return`` / ``raise`` / ``refresh`` / ``wait``.
    """

    action: str


def plan_after_response(
    status_code: int,
    attempt: int,
    max_retries: int,
    token_refreshed: bool,
) -> RetryPlan:
    """Определяет действие после ответа с данным статусом.

    * ``401`` (если токен ещё не обновляли) → обновить токен и повторить;
    * ``429``/``5xx`` (если есть бюджет попыток) → подождать и повторить;
    * ``>= 400`` → бросить исключение;
    * иначе → вернуть ответ.
    """
    if status_code == 401 and not token_refreshed:
        return RetryPlan(REFRESH)
    if (status_code == 429 or status_code >= 500) and attempt < max_retries:
        return RetryPlan(WAIT)
    if status_code >= 400:
        return RetryPlan(RAISE)
    return RetryPlan(RETURN)


def backoff_delay_seconds(
    attempt: int,
    retry_base_delay_ms: int,
    retry_after: Optional[int],
) -> float:
    """Вычисляет задержку перед повтором (секунды).

    При наличии ``Retry-After`` используется он, иначе экспоненциальный backoff
    ``base * 2**(attempt-1)``. ``attempt`` — номер уже начавшейся попытки (>= 1).
    """
    if retry_after is not None:
        return float(retry_after)
    return float(retry_base_delay_ms * (2 ** (attempt - 1))) / 1000.0
