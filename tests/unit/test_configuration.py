"""Тесты конфигурации."""

from __future__ import annotations

import pytest

from avito_ads import Configuration
from avito_ads.exceptions import ConfigurationError


def test_base_uris():
    config = Configuration.create("id", "secret", 123).production()
    assert config.base_uri == "https://api.avito.ru/ads/"
    assert config.token_url == "https://api.avito.ru/token"
    assert config.sandbox().base_uri == "https://api.avito.ru/ads-sandbox/"


def test_immutability():
    config = Configuration.create("id", "secret", 123)
    changed = config.with_max_retries(9)
    assert changed.max_retries == 9
    assert config.max_retries == 4
    assert changed is not config


def test_rejects_non_positive_account_id():
    with pytest.raises(ConfigurationError):
        Configuration.create("id", "secret", 0)


def test_rejects_empty_credentials():
    with pytest.raises(ConfigurationError):
        Configuration.create("", "secret", 123)
    with pytest.raises(ConfigurationError):
        Configuration.create("id", "", 123)
