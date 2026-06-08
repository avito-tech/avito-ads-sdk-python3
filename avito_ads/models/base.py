"""Базовая модель с безопасным приведением типов полей."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Type, TypeVar

M = TypeVar("M", bound="Model")


class Model:
    """Базовый класс модели, хранящий сырые данные ответа.

    Доступ к полям — через типизированные методы-помощники, которые безопасно
    приводят значения и возвращают ``None`` при отсутствии поля.
    """

    def __init__(self, data: Dict[str, Any]) -> None:
        self._data: Dict[str, Any] = data or {}

    @classmethod
    def from_dict(cls: Type[M], data: Optional[Dict[str, Any]]) -> M:
        """Создаёт модель из словаря (``None`` трактуется как пустой словарь)."""
        return cls(data or {})

    @property
    def raw(self) -> Dict[str, Any]:
        """Доступ к исходному словарю ответа."""
        return self._data

    def get(self, key: str) -> Any:
        return self._data.get(key)

    def _int(self, key: str) -> Optional[int]:
        value = self._data.get(key)
        if value is None:
            return None
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    def _str(self, key: str) -> Optional[str]:
        value = self._data.get(key)
        return None if value is None else str(value)

    def _bool(self, key: str) -> Optional[bool]:
        value = self._data.get(key)
        return None if value is None else bool(value)

    def _float(self, key: str) -> Optional[float]:
        value = self._data.get(key)
        if value is None:
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    def _dict(self, key: str) -> Dict[str, Any]:
        value = self._data.get(key)
        return value if isinstance(value, dict) else {}

    def _list(self, key: str) -> List[Any]:
        value = self._data.get(key)
        return value if isinstance(value, list) else []
