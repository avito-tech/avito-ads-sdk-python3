"""Тесты конструктора договоров."""

from __future__ import annotations

import pytest

from avito_ads import ContractBuilder
from avito_ads.enums import ContractCounterpartyType
from avito_ads.exceptions import ValidationError


def test_valid_service_contract():
    body = (
        ContractBuilder.service()
        .advertiser(987)
        .counterparty_type(ContractCounterpartyType.DIRECT_WITH_ADVERTISER)
        .subject("distribution")
        .reporting_required(True)
        .date("2025-01-01")
        .number("A-1")
        .intermediary({"inn": "7712345678"})
        .build()
    )
    assert body["type"] == "service"
    assert body["description"] == "direct_with_advertiser"
    assert body["number"] == "A-1"
    assert "intermediary" in body


def test_valid_external_contract():
    body = (
        ContractBuilder.external("EXT-1")
        .advertiser(1)
        .counterparty_type("advertiser_intermediary")
        .intermediary({"inn": "1"})
        .build()
    )
    assert body["type"] == "external"
    assert body["cid"] == "EXT-1"


def test_additional_agreement_with_parent_id():
    body = (
        ContractBuilder.intermediary_contract()
        .advertiser(1)
        .counterparty_type("direct_with_advertiser")
        .subject("mediation")
        .object("commercial")
        .reporting_required(True)
        .funds_allocation_to_principal(True)
        .date("2025-03-01")
        .number("DS-1")
        .parent_id(100)
        .build()
    )
    assert body["parentId"] == 100
    assert "intermediary" not in body


def test_service_missing_date_raises():
    with pytest.raises(ValidationError):
        (
            ContractBuilder.service()
            .advertiser(1)
            .counterparty_type("direct_with_advertiser")
            .subject("distribution")
            .reporting_required(True)
            .number("A-1")
            .intermediary({"inn": "1"})
            .build()
        )


def test_external_with_parent_id_raises():
    with pytest.raises(ValidationError):
        (
            ContractBuilder.external("EXT-1")
            .advertiser(1)
            .counterparty_type("advertiser_intermediary")
            .parent_id(5)
            .build()
        )


def test_intermediary_missing_object_raises():
    with pytest.raises(ValidationError):
        (
            ContractBuilder.intermediary_contract()
            .advertiser(1)
            .counterparty_type("direct_with_advertiser")
            .subject("mediation")
            .reporting_required(True)
            .date("2025-01-01")
            .number("N-1")
            .intermediary({"inn": "1"})
            .build()
        )


def test_parent_id_with_intermediary_raises():
    with pytest.raises(ValidationError):
        (
            ContractBuilder.intermediary_contract()
            .advertiser(1)
            .counterparty_type("direct_with_advertiser")
            .subject("mediation")
            .object("commercial")
            .reporting_required(True)
            .funds_allocation_to_principal(False)
            .date("2025-01-01")
            .number("N-1")
            .parent_id(7)
            .intermediary({"inn": "1"})
            .build()
        )


def test_missing_intermediary_without_parent_raises():
    with pytest.raises(ValidationError):
        (
            ContractBuilder.service()
            .advertiser(1)
            .counterparty_type("direct_with_advertiser")
            .subject("distribution")
            .reporting_required(True)
            .date("2025-01-01")
            .number("A-1")
            .build()
        )


def test_invalid_enum_value_raises():
    with pytest.raises(ValidationError):
        ContractBuilder.create().subject("bad-subject")
