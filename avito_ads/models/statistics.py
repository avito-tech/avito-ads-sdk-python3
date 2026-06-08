"""Модели статистики."""

from __future__ import annotations

from typing import List, Optional

from .base import Model


class StatsData(Model):
    """Точка статистики (за день или агрегированная)."""

    @property
    def timestamp(self) -> Optional[str]:
        return self._str("timestamp")

    @property
    def views(self) -> int:
        return self._int("views") or 0

    @property
    def clicks(self) -> int:
        return self._int("clicks") or 0

    @property
    def ctr(self) -> Optional[float]:
        return self._float("ctr")

    @property
    def spend(self) -> int:
        return self._int("spend") or 0

    @property
    def spend_bonus(self) -> int:
        return self._int("spendBonus") or 0

    @property
    def cpm(self) -> Optional[float]:
        return self._float("cpm")

    @property
    def cpc(self) -> Optional[float]:
        return self._float("cpc")

    @property
    def video_views_25(self) -> Optional[int]:
        return self._int("videoViews25")

    @property
    def video_views_50(self) -> Optional[int]:
        return self._int("videoViews50")

    @property
    def video_views_75(self) -> Optional[int]:
        return self._int("videoViews75")

    @property
    def video_views_100(self) -> Optional[int]:
        return self._int("videoViews100")

    @property
    def q25(self) -> Optional[float]:
        return self._float("q25")

    @property
    def q50(self) -> Optional[float]:
        return self._float("q50")

    @property
    def q75(self) -> Optional[float]:
        return self._float("q75")

    @property
    def vtr(self) -> Optional[float]:
        return self._float("vtr")


class EntityStatistic(Model):
    """Статистика по сущности (кампании, группе или креативу)."""

    @property
    def id(self) -> Optional[int]:
        return self._int("id")

    @property
    def name(self) -> Optional[str]:
        return self._str("name")

    @property
    def group_id(self) -> Optional[int]:
        return self._int("groupId")

    @property
    def payment_model(self) -> Optional[str]:
        return self._str("paymentModel")

    @property
    def campaign_type(self) -> Optional[str]:
        return self._str("campaignType")

    @property
    def data(self) -> List[StatsData]:
        return [StatsData.from_dict(row) for row in self._list("data")]

    @property
    def total_data(self) -> StatsData:
        return StatsData.from_dict(self._dict("totalData"))


class CampaignStatisticResult(Model):
    """Результат запроса статистики по кампании со сводками по группам и креативам."""

    @property
    def campaign(self) -> EntityStatistic:
        return EntityStatistic.from_dict(self._dict("campaign"))

    @property
    def groups(self) -> List[EntityStatistic]:
        return [EntityStatistic.from_dict(row) for row in self._list("groups")]

    @property
    def creatives(self) -> List[EntityStatistic]:
        return [EntityStatistic.from_dict(row) for row in self._list("creatives")]
