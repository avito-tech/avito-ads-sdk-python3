"""Тесты фильтров."""

from __future__ import annotations

from avito_ads import CampaignsFilter, CreativesFilter, DateRange
from avito_ads.enums import CampaignStatus


def test_campaigns_filter_builds_dict():
    f = (
        CampaignsFilter()
        .ids([1, 2])
        .statuses([CampaignStatus.ACTIVE.value, CampaignStatus.PAUSED.value])
        .contract_ids([10, 20])
        .created_at(DateRange("2025-01-01", "2025-01-31"))
    )
    data = f.to_dict()
    assert data["ids"] == [1, 2]
    assert data["statuses"] == ["active", "paused"]
    # Поле переименовано в contractIDs.
    assert data["contractIDs"] == [10, 20]
    assert data["createdAt"] == {"from": "2025-01-01", "to": "2025-01-31"}


def test_creatives_filter_renames_keys():
    f = CreativesFilter().group_ids([5]).campaign_ids([7])
    data = f.to_dict()
    assert data["groupIDs"] == [5]
    assert data["campaignIDs"] == [7]


def test_empty_filter_is_empty_dict():
    assert CampaignsFilter().to_dict() == {}
