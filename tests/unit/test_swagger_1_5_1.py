"""Изменения swagger 1.5.1: конверсии и лимит ID в статистике."""

from __future__ import annotations

import json

import pytest

from avito_ads import ConversionGoalType
from avito_ads.exceptions import ValidationError
from avito_ads.models import ConversionData, Conversions, CustomGoal, StatsData

from ..conftest import ACCT_PATH, MockRouter, call

PERIOD = ("2026-11-01", "2026-11-10")
PERIOD_BODY = {"dateFrom": PERIOD[0], "dateTo": PERIOD[1]}


def test_click_in_conversions():
    conversions = StatsData.from_dict({"conversions": {
        "contacts": {
            "totalCount": 5, "webCount": 2, "mavCount": 1, "androidCount": 1, "iosCount": 1,
            "cr": 0.05,
        },
        "subscriptions": {
            "totalCount": 0, "webCount": 0, "mavCount": 0, "androidCount": 0, "iosCount": 0,
            "cr": 0,
        },
        "cpaKopeks": 0,
        "goalType": "contacts",
        "cr": 0.05,
    }}).conversions

    assert isinstance(conversions, Conversions)
    contacts = conversions.contacts
    assert isinstance(contacts, ConversionData)
    assert (contacts.total_count, contacts.web_count, contacts.mav_count) == (5, 2, 1)
    assert (contacts.android_count, contacts.ios_count, contacts.cr) == (1, 1, 0.05)
    assert conversions.subscriptions is not None
    assert conversions.subscriptions.total_count == 0
    assert conversions.subscriptions.cr == 0.0
    assert conversions.cpa_kopeks == 0
    assert conversions.cr == 0.05
    assert conversions.goal_type == ConversionGoalType.CONTACTS
    assert conversions.goal_hits is None
    assert conversions.custom_goal is None


def test_click_out_conversions():
    conversions = Conversions.from_dict({
        "goalHits": 10,
        "cpaKopeks": 1250,
        "goalType": "customGoal",
        "customGoal": {"id": 42, "name": "Заявка"},
        "cr": 0.05,
    })
    assert conversions.goal_hits == 10
    assert conversions.cpa_kopeks == 1250
    assert conversions.goal_type == ConversionGoalType.CUSTOM_GOAL
    assert isinstance(conversions.custom_goal, CustomGoal)
    assert (conversions.custom_goal.id, conversions.custom_goal.name) == (42, "Заявка")
    assert conversions.contacts is None
    assert conversions.subscriptions is None


def test_absent_conversions_and_unknown_goal_type():
    assert StatsData.from_dict({}).conversions is None
    assert StatsData.from_dict({"conversions": None}).conversions is None

    unknown = Conversions.from_dict({"goalType": "brand_new"})
    assert unknown.goal_type == "brand_new"
    assert unknown.cr is None
    assert unknown.cpa_kopeks is None
    assert ConversionGoalType.values() == ["contacts", "subscriptions", "customGoal"]


async def test_include_conversions_is_sent_only_when_requested(clients):
    router = MockRouter()
    router.add_token()
    router.add("POST", f"{ACCT_PATH}/campaigns/1/stats",
               json={"campaign": {}, "groups": [], "creatives": []})
    router.add("POST", f"{ACCT_PATH}/campaigns/1/groups/stats", json={"groups": [
        {"id": 2, "data": [], "totalData": {"conversions": {"goalHits": 3}}},
    ]})
    router.add("POST", f"{ACCT_PATH}/campaigns/1/creatives/stats", json={"creatives": []})
    client = clients(router)

    def last_body():
        return json.loads(router.requests[-1].content)

    await call(client.statistics.campaign(1, *PERIOD, include_conversions=True))
    assert last_body() == {**PERIOD_BODY, "includeConversions": True}
    await call(client.statistics.campaign(1, *PERIOD))
    assert last_body() == PERIOD_BODY

    groups = await call(client.statistics.groups(1, *PERIOD, [2], include_conversions=True))
    assert last_body() == {**PERIOD_BODY, "groupIDs": [2], "includeConversions": True}
    assert groups[0].total_data.conversions.goal_hits == 3
    await call(client.statistics.groups(1, *PERIOD, [2]))
    assert last_body() == {**PERIOD_BODY, "groupIDs": [2]}

    await call(client.statistics.creatives(1, *PERIOD, [3]))
    assert last_body() == {**PERIOD_BODY, "creativeIDs": [3]}


@pytest.mark.parametrize("method", ["groups", "creatives"])
async def test_ids_limit(clients, method):
    router = MockRouter()
    router.add_token()
    router.add("POST", f"{ACCT_PATH}/campaigns/1/{method}/stats", json={method: []})
    client = clients(router)
    stats = getattr(client.statistics, method)

    assert await call(stats(1, *PERIOD, list(range(1, 5001)))) == []
    for ids in ([], list(range(1, 5002))):
        with pytest.raises(ValidationError):
            await call(stats(1, *PERIOD, ids))
