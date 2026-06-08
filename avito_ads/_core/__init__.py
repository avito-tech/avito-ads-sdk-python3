"""Транспортно-независимое ядро SDK (sans-I/O).

Содержит общую логику, используемую и синхронным, и асинхронным режимами:
описание операций, разбор ответов, отображение ошибок и политику повторов.
"""

from __future__ import annotations

from .operations import FilterType, Operation, make_list_request
from .response import ApiResponse

__all__ = ["ApiResponse", "Operation", "FilterType", "make_list_request"]
