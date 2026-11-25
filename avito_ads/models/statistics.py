"""Модели статистики."""

from __future__ import annotations

from typing import List, Optional

from .base import Model, warn_deprecated


class ConversionData(Model):
    """Количество конверсий одного типа (контактов или подписок) с разбивкой по платформам."""

    @property
    def total_count(self) -> int:
        return self._int("totalCount") or 0

    @property
    def web_count(self) -> int:
        return self._int("webCount") or 0

    @property
    def mav_count(self) -> int:
        return self._int("mavCount") or 0

    @property
    def android_count(self) -> int:
        return self._int("androidCount") or 0

    @property
    def ios_count(self) -> int:
        return self._int("iosCount") or 0

    @property
    def cr(self) -> Optional[float]:
        """CR: отношение событий к кликам (0.05 = 5%)."""
        return self._float("cr")


class CustomGoal(Model):
    """Главная цель click-out кампании."""

    @property
    def id(self) -> Optional[int]:
        return self._int("id")

    @property
    def name(self) -> Optional[str]:
        return self._str("name")


class Conversions(Model):
    """Конверсии кампании или группы.

    ``None`` в поле означает, что API не вернул значение; ноль — что значение
    известно и равно нулю.
    """

    @property
    def contacts(self) -> Optional[ConversionData]:
        """Контакты; только для click-in кампаний."""
        return self._model("contacts", ConversionData)

    @property
    def subscriptions(self) -> Optional[ConversionData]:
        """Подписки; только для click-in кампаний."""
        return self._model("subscriptions", ConversionData)

    @property
    def goal_hits(self) -> Optional[int]:
        """Количество событий главной цели click-out кампании."""
        return self._int("goalHits")

    @property
    def cpa_kopeks(self) -> Optional[int]:
        """Стоимость целевого действия в копейках."""
        return self._int("cpaKopeks")

    @property
    def goal_type(self) -> Optional[str]:
        """Целевое действие, по которому рассчитаны CPA и CR.

        Значения — :class:`~avito_ads.enums.ConversionGoalType`; неизвестное
        значение возвращается строкой как есть.
        """
        return self._str("goalType")

    @property
    def custom_goal(self) -> Optional[CustomGoal]:
        """Главная цель click-out кампании."""
        return self._model("customGoal", CustomGoal)

    @property
    def cr(self) -> Optional[float]:
        """CR: отношение целевых событий к кликам (0.05 = 5%)."""
        return self._float("cr")


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
    def spend_kopeks(self) -> Optional[int]:
        """Потрачено денег в копейках (``spendKopeks``); ``None``, если поля нет в ответе."""
        return self._int("spendKopeks")

    @property
    def spend_bonus_kopeks(self) -> Optional[int]:
        """Потрачено бонусов в копейках (``spendBonusKopeks``); ``None``, если поля нет."""
        return self._int("spendBonusKopeks")

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

    @property
    def conversions(self) -> Optional[Conversions]:
        """Конверсии за день или за период.

        ``None``, если конверсии не запрошены (``include_conversions``) или данных
        нет. В статистике креативов всегда ``None``.
        """
        return self._model("conversions", Conversions)


class EntityStatistic(Model):
    """Статистика по сущности: общая часть кампании, группы и креатива.

    Конкретные ответы — :class:`CampaignStatistic`, :class:`GroupStatistic` и
    :class:`CreativeStatistic`.
    """

    @property
    def id(self) -> Optional[int]:
        return self._int("id")

    @property
    def name(self) -> Optional[str]:
        return self._str("name")

    @property
    def group_id(self) -> Optional[int]:
        """ID группы креатива.

        .. deprecated:: 1.4.0
            Поле есть только в статистике креатива — :class:`CreativeStatistic`.
        """
        warn_deprecated("EntityStatistic.group_id", "поле есть только у CreativeStatistic.")
        return self._int("groupId")

    @property
    def payment_model(self) -> Optional[str]:
        """Модель оплаты.

        .. deprecated:: 1.4.0
            Поле есть только в статистике кампании — :class:`CampaignStatistic`.
        """
        warn_deprecated("EntityStatistic.payment_model", "поле есть только у CampaignStatistic.")
        return self._str("paymentModel")

    @property
    def campaign_type(self) -> Optional[str]:
        """Тип кампании.

        .. deprecated:: 1.4.0
            Поле есть только в статистике кампании — :class:`CampaignStatistic`.
        """
        warn_deprecated("EntityStatistic.campaign_type", "поле есть только у CampaignStatistic.")
        return self._str("campaignType")

    @property
    def data(self) -> List[StatsData]:
        return [StatsData.from_dict(row) for row in self._list("data")]

    @property
    def total_data(self) -> StatsData:
        return StatsData.from_dict(self._dict("totalData"))


class CampaignStatistic(EntityStatistic):
    """Статистика кампании (с моделью оплаты и типом кампании)."""

    @property
    def payment_model(self) -> Optional[str]:
        return self._str("paymentModel")

    @property
    def campaign_type(self) -> Optional[str]:
        return self._str("campaignType")


class GroupStatistic(EntityStatistic):
    """Статистика группы."""


class CreativeStatistic(EntityStatistic):
    """Статистика креатива (с ID группы)."""

    @property
    def group_id(self) -> Optional[int]:
        return self._int("groupId")


class CampaignStatisticResult(Model):
    """Результат запроса статистики по кампании со сводками по группам и креативам."""

    @property
    def campaign(self) -> CampaignStatistic:
        return CampaignStatistic.from_dict(self._dict("campaign"))

    @property
    def groups(self) -> List[GroupStatistic]:
        return self._models("groups", GroupStatistic)

    @property
    def creatives(self) -> List[CreativeStatistic]:
        return self._models("creatives", CreativeStatistic)
