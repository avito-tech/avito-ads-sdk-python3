"""Типизированные модели ответов API."""

from __future__ import annotations

from .account import Account, Balance
from .advertiser import Advertiser
from .base import Model
from .campaign import Campaign
from .child_account import ChildAccount
from .contract import Contract
from .created import (
    CreatedAccount,
    CreatedAdvertiser,
    CreatedChildAccount,
    CreatedContract,
)
from .creative import Creative, KKTUFieldValue
from .group import FrequencyRule, Group
from .statistics import (
    CampaignStatistic,
    CampaignStatisticResult,
    CreativeStatistic,
    EntityStatistic,
    GroupStatistic,
    StatsData,
)
from .user import User

__all__ = [
    "Model",
    "Account",
    "Balance",
    "Advertiser",
    "Campaign",
    "ChildAccount",
    "Contract",
    "CreatedAccount",
    "CreatedAdvertiser",
    "CreatedChildAccount",
    "CreatedContract",
    "Creative",
    "KKTUFieldValue",
    "Group",
    "FrequencyRule",
    "CampaignStatistic",
    "CampaignStatisticResult",
    "CreativeStatistic",
    "EntityStatistic",
    "GroupStatistic",
    "StatsData",
    "User",
]
