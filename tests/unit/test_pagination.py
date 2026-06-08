"""Тесты пагинации."""

from __future__ import annotations

from avito_ads.pagination import ListRequest, PaginatedResult, iterate_pages


def test_paginated_result_basics():
    result = PaginatedResult(total=3, items=["a", "b"], page=1, limit=2, api_point_balance=100)
    assert result.total == 3
    assert len(result) == 2
    assert result.has_next_page() is True
    assert result.api_point_balance == 100
    assert list(result) == ["a", "b"]


def test_has_next_page_false_on_last_page():
    result = PaginatedResult(total=3, items=["c"], page=2, limit=2)
    assert result.has_next_page() is False


def test_iterate_walks_all_pages():
    served = []

    def loader(req: ListRequest) -> PaginatedResult:
        served.append(req.page)
        if req.page == 1:
            return PaginatedResult(3, ["a", "b"], 1, 2, 100)
        return PaginatedResult(3, ["c"], 2, 2, 99)

    items = list(iterate_pages(loader, ListRequest(filter={}, limit=2, page=1)))
    assert items == ["a", "b", "c"]
    assert served == [1, 2]


def test_iterate_stops_on_empty_page():
    def loader(req: ListRequest) -> PaginatedResult:
        return PaginatedResult(0, [], req.page, 20, 100)

    assert list(iterate_pages(loader, ListRequest(filter={}, limit=20, page=1))) == []
