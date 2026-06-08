"""Тесты ресурсов (sync + async): пути, методы, тело запроса, валидация, пагинация."""

from __future__ import annotations

import pytest

from avito_ads import ContractBuilder
from avito_ads.exceptions import ValidationError
from avito_ads.models import Campaign

from ..conftest import ACCT_PATH, MockRouter, call, collect


async def test_get_balance_path_and_auth(clients):
    router = MockRouter()
    router.add_token()
    router.add("GET", f"{ACCT_PATH}/balance", json={"balance": 15000, "bonusBalance": 500},
               headers={"Api-Point-Balance": "4999"})
    client = clients(router)

    balance = await call(client.account.get_balance())
    assert balance.balance == 15000
    assert router.last.method == "GET"
    assert router.last.url.path == f"{ACCT_PATH}/balance"


async def test_campaigns_list_parses_and_sends_empty_filter_as_object(clients):
    router = MockRouter()
    router.add_token()
    router.add("POST", f"{ACCT_PATH}/campaigns", json={
        "total": 2,
        "campaigns": [
            {"id": 1, "name": "Кампания 1", "status": "active"},
            {"id": 2, "name": "Кампания 2", "status": "paused"},
        ],
    })
    client = clients(router)

    result = await call(client.campaigns.list())
    assert result.total == 2
    assert len(result) == 2
    assert isinstance(result.items[0], Campaign)
    assert result.items[0].name == "Кампания 1"
    assert result.api_point_balance is None

    assert router.last.method == "POST"
    assert router.last.url.path == f"{ACCT_PATH}/campaigns"
    body = router.last_body()
    # Пустой фильтр должен быть объектом {}, а не массивом [].
    assert body["filter"] == {}
    assert body["page"] == 1
    assert body["limit"] == 20


async def test_campaigns_iterate_walks_pages(clients):
    router = MockRouter()
    router.add_token()
    router.add("POST", f"{ACCT_PATH}/campaigns", json={
        "total": 3, "campaigns": [{"id": 1, "name": "a"}, {"id": 2, "name": "b"}]
    })
    router.add("POST", f"{ACCT_PATH}/campaigns", json={
        "total": 3, "campaigns": [{"id": 3, "name": "c"}]
    })
    client = clients(router)

    names = [c.name for c in await collect(client.campaigns.iterate(limit=2))]
    assert names == ["a", "b", "c"]


async def test_change_budget_rejects_zero(clients):
    router = MockRouter()
    router.add_token()
    client = clients(router)
    with pytest.raises(ValidationError):
        await call(client.groups.change_budget(10, 0))


async def test_transfer_funds_rejects_below_one(clients):
    router = MockRouter()
    router.add_token()
    client = clients(router)
    with pytest.raises(ValidationError):
        await call(client.child_accounts.transfer_funds(999, 0))


async def test_transfer_funds_sends_body(clients):
    router = MockRouter()
    router.add_token()
    router.add("POST", f"{ACCT_PATH}/funds-transfer", json={})
    client = clients(router)

    await call(client.child_accounts.transfer_funds(987654321, 5000))
    assert router.last_body() == {"accountIdTo": 987654321, "amount": 5000}


async def test_statistics_rejects_period_over_100_days(clients):
    router = MockRouter()
    router.add_token()
    client = clients(router)
    with pytest.raises(ValidationError):
        await call(client.statistics.campaign(1, "2025-01-01", "2025-06-01"))


async def test_statistics_campaign_parses_and_sends_dates(clients):
    router = MockRouter()
    router.add_token()
    router.add("POST", f"{ACCT_PATH}/campaigns/1/stats", json={
        "campaign": {
            "id": 1,
            "name": "Промо",
            "data": [{"timestamp": "2025-01-01", "views": 100, "clicks": 5}],
            "totalData": {"views": 100, "clicks": 5},
        },
        "groups": [],
        "creatives": [],
    })
    client = clients(router)

    result = await call(client.statistics.campaign(1, "2025-01-01", "2025-01-31"))
    assert result.campaign.name == "Промо"
    assert result.campaign.total_data.views == 100

    assert router.last.url.path == f"{ACCT_PATH}/campaigns/1/stats"
    body = router.last_body()
    assert body["dateFrom"] == "2025-01-01"
    assert body["dateTo"] == "2025-01-31"


async def test_users_list_parsed(clients):
    router = MockRouter()
    router.add_token()
    router.add("GET", f"{ACCT_PATH}/users", json={
        "total": 1, "users": [{"id": 42, "role": "admin", "hasLoggedIn": True}]
    })
    client = clients(router)

    users = await call(client.users.list())
    assert len(users) == 1
    assert users[0].id == 42
    assert users[0].role == "admin"
    assert users[0].has_logged_in is True


async def test_add_user_rejects_invalid_role(clients):
    router = MockRouter()
    router.add_token()
    client = clients(router)
    with pytest.raises(ValidationError):
        await call(client.users.add(42, "superhero"))


async def test_delete_user_uses_delete_method_and_path(clients):
    router = MockRouter()
    router.add_token()
    router.add("DELETE", f"{ACCT_PATH}/delete-user/42", text="")
    client = clients(router)

    await call(client.users.delete(42))
    assert router.last.method == "DELETE"
    assert router.last.url.path == f"{ACCT_PATH}/delete-user/42"


async def test_create_contract_via_builder_sends_built_body(clients):
    router = MockRouter()
    router.add_token()
    router.add("POST", f"{ACCT_PATH}/create-contract", json={"id": 555})
    client = clients(router)

    builder = (
        ContractBuilder.external("EXT-1")
        .advertiser(987)
        .counterparty_type("advertiser_intermediary")
        .intermediary({"inn": "1"})
    )
    created = await call(client.contracts.create(builder))
    assert created.id == 555
    body = router.last_body()
    assert body["type"] == "external"
    assert body["cid"] == "EXT-1"


async def test_sandbox_environment_uses_sandbox_path(clients):
    router = MockRouter()
    router.add_token()
    router.add("GET", "/ads-sandbox/v1/account/123456789/balance",
               json={"balance": 1, "bonusBalance": 0})
    client = clients(router, sandbox=True)

    await call(client.account.get_balance())
    assert router.last.url.path == "/ads-sandbox/v1/account/123456789/balance"
