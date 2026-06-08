"""Модель токена доступа."""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Dict

from ..exceptions import AuthenticationError


@dataclass(frozen=True)
class AccessToken:
    """Токен доступа с временем истечения (абсолютная отметка времени, секунды).

    :param token: значение токена.
    :param expires_at: абсолютное время истечения (Unix timestamp, сек).
    :param token_type: тип токена, обычно ``Bearer``.
    """

    token: str
    expires_at: float
    token_type: str = "Bearer"

    @classmethod
    def from_response(cls, data: Dict[str, Any], now: float) -> "AccessToken":
        """Создаёт токен из ответа эндпоинта ``/token``.

        :param data: разобранное тело ответа.
        :param now: текущее время (Unix timestamp), от которого считается истечение.
        :raises AuthenticationError: если в ответе нет поля ``access_token``.
        """
        token = data.get("access_token")
        if not token or not isinstance(token, str):
            raise AuthenticationError(
                "Ответ эндпоинта /token не содержит access_token."
            )
        expires_in = data.get("expires_in", 86400)
        try:
            expires_in = int(expires_in)
        except (TypeError, ValueError):
            expires_in = 86400
        token_type = data.get("token_type", "Bearer")
        return cls(token=token, expires_at=now + expires_in, token_type=str(token_type))

    def is_expired(self, leeway: int = 0, now: float = None) -> bool:  # type: ignore[assignment]
        """Проверяет, истёк ли токен с учётом запаса ``leeway`` (секунды)."""
        current = time.time() if now is None else now
        return current >= (self.expires_at - leeway)

    def authorization_header(self) -> str:
        """Готовое значение заголовка ``Authorization``."""
        return f"{self.token_type} {self.token}"

    def to_dict(self) -> Dict[str, Any]:
        """Сериализация для сохранения в хранилище."""
        return {
            "token": self.token,
            "expires_at": self.expires_at,
            "token_type": self.token_type,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AccessToken":
        """Десериализация из хранилища."""
        return cls(
            token=str(data["token"]),
            expires_at=float(data["expires_at"]),
            token_type=str(data.get("token_type", "Bearer")),
        )
