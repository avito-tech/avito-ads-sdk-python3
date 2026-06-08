"""Тесты перечислений."""

from __future__ import annotations

import pytest

from avito_ads import CampaignStatus, ContractType, LegalRole, LegalType, UserRole
from avito_ads.exceptions import ValidationError


def test_values():
    assert LegalType.values() == ["ul", "ip"]
    assert UserRole.values() == ["admin", "viewer"]
    assert LegalRole.values() == ["rd", "ra", "rr"]


def test_is_valid():
    assert CampaignStatus.is_valid("active")
    assert CampaignStatus.is_valid(CampaignStatus.ACTIVE)
    assert not CampaignStatus.is_valid("unknown")


def test_assert_valid_returns_string():
    assert ContractType.assert_valid("service") == "service"
    assert ContractType.assert_valid(ContractType.EXTERNAL) == "external"


def test_assert_valid_raises():
    with pytest.raises(ValidationError):
        ContractType.assert_valid("nope")
