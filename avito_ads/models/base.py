"""Базовая модель с безопасным приведением типов полей."""

from __future__ import annotations

import warnings
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

    def _str_list(self, key: str) -> List[str]:
        """Список строк; ``null``/отсутствие — пустой список, ``None`` внутри пропускается."""
        return [str(item) for item in self._list(key) if item is not None]

    def _int_list(self, key: str) -> List[int]:
        """Список целых; нечисловые элементы пропускаются."""
        result: List[int] = []
        for item in self._list(key):
            try:
                result.append(int(item))
            except (TypeError, ValueError):
                continue
        return result

    def _models(self, key: str, model: Type[M]) -> List[M]:
        """Список вложенных объектов, обёрнутых в модель ``model``."""
        return [model.from_dict(row) for row in self._list(key) if isinstance(row, dict)]


def warn_deprecated(name: str, hint: str) -> None:
    """Выдаёт ``DeprecationWarning`` при чтении устаревшего поля ответа."""
    warnings.warn(f"{name} устарело: {hint}", DeprecationWarning, stacklevel=3)
