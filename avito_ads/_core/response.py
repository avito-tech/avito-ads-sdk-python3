"""Объект-обёртка над ответом API (общий для sync и async)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class ApiResponse:
    """Разобранный ответ API.

    :param status_code: HTTP-код ответа.
    :param data: разобранное тело (JSON-объект) или пустой словарь.
    :param api_point_balance: остаток лимита из заголовка ``Api-Point-Balance``.
    """

    status_code: int
    data: Dict[str, Any]
    api_point_balance: Optional[int] = None
