"""Тесты постраничного запроса."""

from __future__ import annotations

import json

import pytest

from avito_ads.exceptions import ValidationError
from avito_ads.pagination import ListRequest


def test_empty_filter_serializes_as_object():
    request = ListRequest(filter={}, limit=20, page=1)
    body = request.to_dict()
    assert isinstance(body["filter"], dict)
    # Пустой словарь сериализуется в JSON как {} (а не [] ).
    assert json.dumps(body["filter"]) == "{}"


def test_non_empty_filter_kept():
    request = ListRequest(filter={"ids": [1, 2]}, limit=50, page=2)
    assert request.to_dict()["filter"] == {"ids": [1, 2]}
    assert request.limit == 50
    assert request.page == 2


def test_with_page_clones():
    request = ListRequest(filter={}, limit=20, page=1)
    assert request.with_page(5).page == 5
    assert request.page == 1


@pytest.mark.parametrize("limit,page", [(0, 1), (101, 1), (20, 0)])
def test_validation(limit, page):
    with pytest.raises(ValidationError):
        ListRequest(filter={}, limit=limit, page=page)
