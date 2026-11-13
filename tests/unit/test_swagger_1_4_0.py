"""Изменения swagger 1.4.0: новые поля, статусы, 409, 207 и терпимость к новым значениям."""

from __future__ import annotations

import warnings

import pytest

from avito_ads import (
    BudgetFrequency,
    CampaignBudgetFrequency,
    CampaignStatus,
    CreativesStatus,
    FrequencyPeriod,
    LegalType,
)
from avito_ads.exceptions import ApiError, ConflictError, ValidationError
from avito_ads.models import (
    Balance,
    Campaign,
    CampaignStatistic,
    Contract,
    CreativeStatistic,
    EntityStatistic,
    Group,
    GroupStatistic,
    StatsData,
)
from avito_ads.models.creative import Creative

from ..conftest import ACCT_PATH, MockRouter, call

SANDBOX_ACCT = "/ads-sandbox/v1/account/123456789"


# --- Политика неизвестных значений -------------------------------------------


async def test_unknown_enum_values_and_reasons_are_kept_as_strings(clients):
    router = MockRouter()
    router.add_token()
    router.add("POST", f"{ACCT_PATH}/campaigns", json={
        "total": 1,
        "campaigns": [{
            "id": 1,
            "status": "some_future_status",
            "budgetFrequency": "weekly_future",
            "statusReasons": ["manual", "brand_new_reason"],
            "topStatusReason": "brand_new_reason",
        }],
    })
    router.add("POST", f"{ACCT_PATH}/groups", json={
        "total": 1,
        "groups": [{"id": 2, "status": "x_status", "budgetFrequency": "x_freq",
                    "statusReasons": ["x_reason"], "topStatusReason": "",
                    "frequencyRules": [{"count": 3, "period": "x_period"}]}],
    })
    router.add("POST", f"{ACCT_PATH}/creatives", json={
        "total": 1,
        "creatives": [{"id": 3, "status": "x_status", "statusReasons": [], "topStatusReason": ""}],
    })
    client = clients(router)

    campaign = (await call(client.campaigns.list())).items[0]
    assert campaign.status == "some_future_status"
    assert campaign.budget_frequency == "weekly_future"
    assert campaign.status_reasons == ["manual", "brand_new_reason"]
    assert campaign.top_status_reason == "brand_new_reason"

    group = (await call(client.groups.list())).items[0]
    assert group.status == "x_status"
    assert group.budget_frequency == "x_freq"
    assert group.status_reasons == ["x_reason"]
    assert group.frequency_rules[0].period == "x_period"

    creative = (await call(client.creatives.list())).items[0]
    assert creative.status == "x_status"
    assert creative.status_reasons == []
    assert creative.top_status_reason == ""


def test_new_status_values():
    for value in ("will_launch_soon", "partially_active", "will_stop_soon", "pausing",
                  "unpausing"):
        assert CampaignStatus.is_valid(value)
    for value in ("will_launch_soon", "pausing", "unpausing"):
        assert CreativesStatus.is_valid(value)
    assert CampaignBudgetFrequency.values() == ["daily", "entirePeriod", "mixed"]
    assert BudgetFrequency.values() == ["daily", "entirePeriod"]
    assert FrequencyPeriod.values() == ["no_limit", "day", "week", "month"]


# --- Деньги ------------------------------------------------------------------


def test_campaign_budget_absent_null_and_zero_are_distinct():
    mixed = Campaign.from_dict({"budgetFrequency": "mixed"})
    assert mixed.budget is None
    assert mixed.budget_kopeks is None
    assert mixed.budget_frequency == CampaignBudgetFrequency.MIXED

    null = Campaign.from_dict({"budget": None, "budgetKopeks": None})
    assert null.budget is None
    assert null.budget_kopeks is None

    empty = Campaign.from_dict({"budget": 0, "budgetKopeks": 0, "budgetFrequency": "daily"})
    assert empty.budget == 0
    assert empty.budget_kopeks == 0


def test_campaign_new_fields_and_defaults():
    campaign = Campaign.from_dict({"performanceAdditionalAgreementID": 77, "budgetKopeks": 1050})
    assert campaign.performance_additional_agreement_id == 77
    assert campaign.budget_kopeks == 1050
    assert campaign.status_reasons == []
    assert campaign.top_status_reason == ""


def test_kopeks_fields():
    balance = Balance.from_dict(
        {"balance": 10, "balanceKopeks": 1050, "bonusBalance": 1, "bonusBalanceKopeks": 150}
    )
    assert balance.balance_kopeks == 1050
    assert balance.bonus_balance_kopeks == 150

    stats = StatsData.from_dict({"spend": 1, "spendKopeks": 125, "spendBonusKopeks": 5})
    assert stats.spend_kopeks == 125
    assert stats.spend_bonus_kopeks == 5
    assert StatsData.from_dict({}).spend_kopeks is None


# --- Группа ------------------------------------------------------------------


GROUP = {
    "id": 5,
    "budgetKopeks": 100000,
    "priceKopeks": 2550,
    "budgetFrequency": "daily",
    "frequencyRules": [{"count": 3, "period": "day"}, {"count": 10, "period": "week"}],
    "frequencyCount": 3,
    "frequencyPeriod": "day",
    "actions": ["pause", "edit"],
    "activitySchedule": {"monday": [9, 10, 11], "sunday": []},
    "audienceType": "basic",
    "format": "native",
    "pace": "even",
    "periodStartAt": "2026-11-01T00:00:00Z",
    "periodEndAt": None,
    "periodTimezone": "Europe/Moscow",
    "priceControl": "manual",
    "scheduleType": "custom",
    "startASAP": True,
    "userID": 42,
    "targetingAgeIDs": [1, 2],
    "targetingAudienceIDs": ["a1"],
    "targetingFamilyStatusIDs": [3],
    "targetingGenderIDs": [1],
    "targetingIncomeIDs": [4],
    "targetingInterestIDs": ["i1", "i2"],
    "targetingLocationIDs": [637640],
    "targetingParentStatusIDs": [5],
    "statusReasons": ["insufficient_funds"],
    "topStatusReason": "insufficient_funds",
}


def test_group_new_fields():
    group = Group.from_dict(GROUP)
    assert group.budget_kopeks == 100000
    assert group.price_kopeks == 2550
    assert group.budget_frequency == BudgetFrequency.DAILY
    assert [(r.count, r.period) for r in group.frequency_rules] == [(3, "day"), (10, "week")]
    assert group.actions == ["pause", "edit"]
    assert group.activity_schedule == {"monday": [9, 10, 11], "sunday": []}
    assert group.audience_type == "basic"
    assert group.format == "native"
    assert group.pace == "even"
    assert group.period_start_at == "2026-11-01T00:00:00Z"
    assert group.period_end_at is None
    assert group.period_timezone == "Europe/Moscow"
    assert group.price_control == "manual"
    assert group.schedule_type == "custom"
    assert group.start_asap is True
    assert group.user_id == 42
    assert group.targeting_age_ids == [1, 2]
    assert group.targeting_audience_ids == ["a1"]
    assert group.targeting_family_status_ids == [3]
    assert group.targeting_gender_ids == [1]
    assert group.targeting_income_ids == [4]
    assert group.targeting_interest_ids == ["i1", "i2"]
    assert group.targeting_location_ids == [637640]
    assert group.targeting_parent_status_ids == [5]
    assert group.status_reasons == ["insufficient_funds"]
    assert group.top_status_reason == "insufficient_funds"


def test_group_legacy_frequency_fields_are_deprecated():
    group = Group.from_dict(GROUP)
    with pytest.warns(DeprecationWarning, match="frequency_rules"):
        assert group.frequency_count == 3
    with pytest.warns(DeprecationWarning, match="frequency_rules"):
        assert group.frequency_period == "day"


# --- Креатив и договор --------------------------------------------------------


def test_creative_new_fields_and_deprecated_legal_info():
    creative = Creative.from_dict({
        "kktuFields": [{"key": "kktu", "value": "30.10.1"}],
        "landingID": 9,
        "originUrl": "https://example.com/?utm=1",
        "previewUrl": "https://example.com/preview",
        "userID": 7,
        "legalInfo": {"kktu": "30.10.1"},
    })
    assert [(f.key, f.value) for f in creative.kktu_fields] == [("kktu", "30.10.1")]
    assert creative.landing_id == 9
    assert creative.origin_url == "https://example.com/?utm=1"
    assert creative.preview_url == "https://example.com/preview"
    assert creative.user_id == 7
    with pytest.warns(DeprecationWarning, match="kktu_fields"):
        assert creative.legal_info == {"kktu": "30.10.1"}


def test_contract_flags():
    contract = Contract.from_dict({"isAgentActingForPublisher": True, "isCreativeReporter": None})
    assert contract.is_agent_acting_for_publisher is True
    assert contract.is_creative_reporter is None


# --- Статистика ---------------------------------------------------------------


async def test_statistics_specific_types(clients):
    router = MockRouter()
    router.add_token()
    router.add("POST", f"{ACCT_PATH}/campaigns/1/groups/stats",
               json={"groups": [{"id": 2, "name": "G", "data": [], "totalData": {}}]})
    router.add("POST", f"{ACCT_PATH}/campaigns/1/creatives/stats",
               json={"creatives": [{"id": 3, "groupId": 2, "data": [], "totalData": {}}]})
    client = clients(router)

    groups = await call(client.statistics.groups(1, "2026-11-01", "2026-11-02", [2]))
    assert isinstance(groups[0], GroupStatistic)
    creatives = await call(client.statistics.creatives(1, "2026-11-01", "2026-11-02", [3]))
    assert isinstance(creatives[0], CreativeStatistic)
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        assert creatives[0].group_id == 2


def test_campaign_statistic_fields_without_warning_and_legacy_access_warns():
    campaign = CampaignStatistic.from_dict({"paymentModel": "CPC", "campaignType": "video"})
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        assert campaign.payment_model == "CPC"
        assert campaign.campaign_type == "video"
    assert isinstance(campaign, EntityStatistic)
    with pytest.warns(DeprecationWarning):
        assert GroupStatistic.from_dict({}).payment_model is None


# --- 409 у change-budget / change-price ---------------------------------------


@pytest.mark.parametrize(
    "path,method_name,value",
    [("change-budget", "change_budget", 1000), ("change-price", "change_price", 25)],
)
async def test_conflict_409_raises_conflict_error(clients, path, method_name, value):
    router = MockRouter()
    router.add_token()
    router.add("POST", f"{ACCT_PATH}/group/5/{path}",
               json={"code": "conflict", "message": "Конфликт версий группы"}, status=409)
    client = clients(router)

    with pytest.raises(ConflictError) as info:
        await call(getattr(client.groups, method_name)(5, value))
    assert isinstance(info.value, ApiError)
    assert info.value.status_code == 409
    assert info.value.error_code == "conflict"
    assert str(info.value) == "Конфликт версий группы"


# --- Sandbox: 207 и warnings, обязательный legal_type -------------------------


def _create_sandbox(client, **overrides):  # type: ignore[no-untyped-def]
    kwargs = {
        "inn": "7712345678",
        "short_name": "Тест",
        "long_name": "ООО Тест",
        "ogrn": "1177746123456",
        "legal_address": "г. Москва",
        "actual_address": None,
        "contact": {"name": "Иван", "phone": "+79001234567"},
        "legal_type": LegalType.UL,
    }
    kwargs.update(overrides)
    return client.account.create_sandbox_account(**kwargs)


async def test_sandbox_207_is_success_with_warnings(clients):
    router = MockRouter()
    router.add_token()
    router.add("POST", SANDBOX_ACCT, status=207,
               json={"accountID": 555, "warnings": ["contracts: not prepared"]})
    client = clients(router, sandbox=True)

    created = await call(_create_sandbox(client))
    assert created.account_id == 555
    assert created.warnings == ["contracts: not prepared"]
    body = router.last_body()
    assert body["legalType"] == "ul"
    assert "actualAddress" not in body


async def test_sandbox_200_has_empty_warnings(clients):
    router = MockRouter()
    router.add_token()
    router.add("POST", SANDBOX_ACCT, json={"accountID": 556, "warnings": []})
    client = clients(router, sandbox=True)

    created = await call(_create_sandbox(client, actual_address="г. Москва, д. 2"))
    assert created.warnings == []
    assert router.last_body()["actualAddress"] == "г. Москва, д. 2"


async def test_sandbox_requires_valid_legal_type(clients):
    router = MockRouter()
    client = clients(router, sandbox=True)

    with pytest.raises(ValidationError):
        await call(_create_sandbox(client, legal_type=None))
    with pytest.raises(ValidationError):
        await call(_create_sandbox(client, legal_type="llc"))
    assert router.requests == []
