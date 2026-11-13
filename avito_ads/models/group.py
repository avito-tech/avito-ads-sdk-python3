"""Модель группы объявлений."""

from __future__ import annotations

from typing import Dict, List, Optional

from .base import Model, warn_deprecated

_WEEKDAYS = ("monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday")


class FrequencyRule(Model):
    """Правило частотного ограничения: не более ``count`` показов за ``period``."""

    @property
    def count(self) -> Optional[int]:
        """Количество показов за период."""
        return self._int("count")

    @property
    def period(self) -> Optional[str]:
        """Период: ``no_limit``, ``day``, ``week`` или ``month``.

        См. :class:`~avito_ads.enums.FrequencyPeriod`.
        """
        return self._str("period")


class Group(Model):
    """Группа объявлений.

    Значения перечислений (``status``, ``budget_frequency``, ``format``,
    ``pace`` и др.) и коды причин возвращаются строками как есть: новые
    значения, добавленные в API, не вызывают ошибку.
    """

    @property
    def id(self) -> Optional[int]:
        return self._int("id")

    @property
    def name(self) -> Optional[str]:
        return self._str("name")

    @property
    def account_id(self) -> Optional[int]:
        return self._int("accountID")

    @property
    def campaign_id(self) -> Optional[int]:
        return self._int("campaignID")

    @property
    def user_id(self) -> Optional[int]:
        """ID пользователя, создавшего группу (``userID``)."""
        return self._int("userID")

    @property
    def status(self) -> Optional[str]:
        """Статус группы (см. :class:`~avito_ads.enums.GroupsStatus`)."""
        return self._str("status")

    @property
    def status_reasons(self) -> List[str]:
        """Все коды причин текущего статуса (``[]``, если причин нет)."""
        return self._str_list("statusReasons")

    @property
    def top_status_reason(self) -> str:
        """Главная причина текущего статуса (``""``, если не определена)."""
        return self._str("topStatusReason") or ""

    @property
    def actions(self) -> List[str]:
        """Доступные действия с группой."""
        return self._str_list("actions")

    @property
    def budget(self) -> Optional[int]:
        """Бюджет группы в рублях с НДС."""
        return self._int("budget")

    @property
    def budget_kopeks(self) -> Optional[int]:
        """Бюджет группы в копейках с НДС (``budgetKopeks``)."""
        return self._int("budgetKopeks")

    @property
    def budget_frequency(self) -> Optional[str]:
        """Частота расходования бюджета: ``daily`` или ``entirePeriod``.

        См. :class:`~avito_ads.enums.BudgetFrequency`.
        """
        return self._str("budgetFrequency")

    @property
    def price(self) -> Optional[int]:
        """Цена в рублях с НДС."""
        return self._int("price")

    @property
    def price_kopeks(self) -> Optional[int]:
        """Цена в копейках с НДС (``priceKopeks``)."""
        return self._int("priceKopeks")

    @property
    def price_control(self) -> Optional[str]:
        """Контроль цены: ``manual`` или ``auto`` (:class:`~avito_ads.enums.GroupPriceControl`)."""
        return self._str("priceControl")

    @property
    def frequency_rules(self) -> List[FrequencyRule]:
        """Правила частотного ограничения (``frequencyRules``)."""
        return self._models("frequencyRules", FrequencyRule)

    @property
    def frequency_count(self) -> Optional[int]:
        """Частота показов первого правила.

        .. deprecated:: 1.4.0
            Используйте :attr:`frequency_rules`; поле соответствует первому правилу.
        """
        warn_deprecated("Group.frequency_count", "используйте Group.frequency_rules.")
        return self._int("frequencyCount")

    @property
    def frequency_period(self) -> Optional[str]:
        """Период частоты первого правила.

        .. deprecated:: 1.4.0
            Используйте :attr:`frequency_rules`; поле соответствует первому правилу.
        """
        warn_deprecated("Group.frequency_period", "используйте Group.frequency_rules.")
        return self._str("frequencyPeriod")

    @property
    def format(self) -> Optional[str]:
        """Формат группы (см. :class:`~avito_ads.enums.GroupFormat`)."""
        return self._str("format")

    @property
    def audience_type(self) -> Optional[str]:
        """Тип аудитории таргетинга (см. :class:`~avito_ads.enums.AudienceType`)."""
        return self._str("audienceType")

    @property
    def pace(self) -> Optional[str]:
        """Скорость показов: ``asap`` или ``even`` (:class:`~avito_ads.enums.Paces`)."""
        return self._str("pace")

    @property
    def schedule_type(self) -> Optional[str]:
        """Тип расписания показов (см. :class:`~avito_ads.enums.ScheduleType`)."""
        return self._str("scheduleType")

    @property
    def activity_schedule(self) -> Dict[str, List[int]]:
        """Расписание активности: день недели (``monday`` … ``sunday``) -> часы 0–23.

        Отсутствующие в ответе дни в словарь не попадают.
        """
        schedule = Model(self._dict("activitySchedule"))
        return {day: schedule._int_list(day) for day in _WEEKDAYS if day in schedule.raw}

    @property
    def start_asap(self) -> Optional[bool]:
        """Запускать как можно скорее (``startASAP``)."""
        return self._bool("startASAP")

    @property
    def period_start_at(self) -> Optional[str]:
        """Начало периода показов (date-time)."""
        return self._str("periodStartAt")

    @property
    def period_end_at(self) -> Optional[str]:
        """Конец периода показов (date-time)."""
        return self._str("periodEndAt")

    @property
    def period_timezone(self) -> Optional[str]:
        """Таймзона периода показов."""
        return self._str("periodTimezone")

    @property
    def targeting_age_ids(self) -> List[int]:
        """ID возрастных сегментов."""
        return self._int_list("targetingAgeIDs")

    @property
    def targeting_audience_ids(self) -> List[str]:
        """ID аудиторий."""
        return self._str_list("targetingAudienceIDs")

    @property
    def targeting_family_status_ids(self) -> List[int]:
        """ID семейного статуса."""
        return self._int_list("targetingFamilyStatusIDs")

    @property
    def targeting_gender_ids(self) -> List[int]:
        """ID пола."""
        return self._int_list("targetingGenderIDs")

    @property
    def targeting_income_ids(self) -> List[int]:
        """ID доходных сегментов."""
        return self._int_list("targetingIncomeIDs")

    @property
    def targeting_interest_ids(self) -> List[str]:
        """ID интересов."""
        return self._str_list("targetingInterestIDs")

    @property
    def targeting_location_ids(self) -> List[int]:
        """ID локаций."""
        return self._int_list("targetingLocationIDs")

    @property
    def targeting_parent_status_ids(self) -> List[int]:
        """ID родительского статуса."""
        return self._int_list("targetingParentStatusIDs")

    @property
    def payment_model(self) -> Optional[str]:
        return self._str("paymentModel")

    @property
    def campaign_type(self) -> Optional[str]:
        return self._str("campaignType")

    @property
    def advertiser_id(self) -> Optional[int]:
        return self._int("advertiserID")

    @property
    def manager_id(self) -> Optional[int]:
        return self._int("managerID")

    @property
    def have_creative(self) -> Optional[bool]:
        return self._bool("haveCreative")

    @property
    def created_at(self) -> Optional[str]:
        return self._str("createdAt")

    @property
    def updated_at(self) -> Optional[str]:
        return self._str("updatedAt")
