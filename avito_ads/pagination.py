"""Постраничная выборка: запрос, результат и автоматический обход страниц."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import (
    Any,
    AsyncIterator,
    Awaitable,
    Callable,
    Dict,
    Generic,
    Iterator,
    List,
    Optional,
    TypeVar,
)

from .exceptions import ValidationError

T = TypeVar("T")

MAX_LIMIT = 100
DEFAULT_LIMIT = 20


@dataclass(frozen=True)
class ListRequest:
    """Параметры постраничного запроса.

    :param filter: словарь фильтра (пустой словарь сериализуется в JSON как ``{}``).
    :param limit: размер страницы, от 1 до 100.
    :param page: номер страницы, начиная с 1.
    """

    filter: Dict[str, Any] = field(default_factory=dict)
    limit: int = DEFAULT_LIMIT
    page: int = 1

    def __post_init__(self) -> None:
        if not 1 <= self.limit <= MAX_LIMIT:
            raise ValidationError(
                f"limit должен быть в диапазоне 1..{MAX_LIMIT}, передано {self.limit}."
            )
        if self.page < 1:
            raise ValidationError(f"page должен быть >= 1, передано {self.page}.")

    def with_page(self, page: int) -> "ListRequest":
        """Возвращает копию запроса с другим номером страницы."""
        return replace(self, page=page)

    def to_dict(self) -> Dict[str, Any]:
        """Тело запроса. Пустой фильтр остаётся пустым словарём → JSON ``{}``."""
        return {"filter": self.filter, "limit": self.limit, "page": self.page}


class PaginatedResult(Generic[T]):
    """Результат одной страницы выборки.

    Поддерживает ``len()`` и итерацию по элементам страницы.
    """

    def __init__(
        self,
        total: int,
        items: List[T],
        page: int,
        limit: int,
        api_point_balance: Optional[int] = None,
    ) -> None:
        self.total = total
        self.items = items
        self.page = page
        self.limit = limit
        self.api_point_balance = api_point_balance

    def __iter__(self) -> Iterator[T]:
        return iter(self.items)

    def __len__(self) -> int:
        return len(self.items)

    def has_next_page(self) -> bool:
        """Есть ли ещё страницы (исходя из ``total``, ``page`` и ``limit``)."""
        return self.page * self.limit < self.total


def iterate_pages(
    loader: Callable[[ListRequest], "PaginatedResult[T]"],
    request: ListRequest,
) -> Iterator[T]:
    """Перебирает все элементы по всем страницам, подгружая их по мере необходимости.

    :param loader: функция, загружающая страницу по :class:`ListRequest`.
    :param request: начальный запрос (страница будет увеличиваться автоматически).
    """
    current = request
    while True:
        result = loader(current)
        if len(result) == 0:
            return
        yield from result.items
        if not result.has_next_page():
            return
        current = current.with_page(current.page + 1)


async def iterate_pages_async(
    loader: Callable[[ListRequest], Awaitable["PaginatedResult[T]"]],
    request: ListRequest,
) -> AsyncIterator[T]:
    """Асинхронный аналог :func:`iterate_pages`.

    :param loader: корутина, загружающая страницу по :class:`ListRequest`.
    :param request: начальный запрос (страница увеличивается автоматически).
    """
    current = request
    while True:
        result = await loader(current)
        if len(result) == 0:
            return
        for item in result.items:
            yield item
        if not result.has_next_page():
            return
        current = current.with_page(current.page + 1)
