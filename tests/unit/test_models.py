"""Тесты моделей."""

from __future__ import annotations

from avito_ads.models import (
    Account,
    Balance,
    CampaignStatisticResult,
    ChildAccount,
    Contract,
    StatsData,
)


def test_account_getters():
    account = Account.from_dict(
        {"inn": "7700000000", "shortName": "ООО Ромашка", "contact": {"name": "Иван"}}
    )
    assert account.inn == "7700000000"
    assert account.short_name == "ООО Ромашка"
    assert account.contact == {"name": "Иван"}
    assert account.kpp is None


def test_balance_casts_to_int():
    balance = Balance.from_dict({"balance": "15000", "bonusBalance": 500})
    assert balance.balance == 15000
    assert balance.bonus_balance == 500


def test_contract_nested_advertisers():
    contract = Contract.from_dict(
        {
            "id": 10,
            "client": {"id": 1, "shortName": "Клиент"},
            "contractor": {"id": 2, "shortName": "Исполнитель"},
        }
    )
    assert contract.client.short_name == "Клиент"
    assert contract.contractor.short_name == "Исполнитель"


def test_child_account_balance():
    child = ChildAccount.from_dict(
        {
            "account": {"id": 55, "shortName": "Дочерний"},
            "balance": {"balance": 1000, "bonusBalance": 0},
        }
    )
    assert child.id == 55
    assert child.short_name == "Дочерний"
    assert child.balance is not None
    assert child.balance.balance == 1000


def test_campaign_statistic_result():
    result = CampaignStatisticResult.from_dict(
        {
            "campaign": {
                "id": 1,
                "name": "Промо",
                "data": [{"views": 100, "clicks": 10}],
                "totalData": {"views": 100, "clicks": 10},
            },
            "groups": [{"id": 2, "name": "Группа", "data": [], "totalData": {}}],
            "creatives": [],
        }
    )
    assert result.campaign.name == "Промо"
    data = result.campaign.data
    assert len(data) == 1
    assert isinstance(data[0], StatsData)
    assert data[0].views == 100
    assert len(result.groups) == 1
    assert result.groups[0].name == "Группа"
