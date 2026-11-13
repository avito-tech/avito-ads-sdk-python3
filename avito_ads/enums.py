"""Перечисления (enum) значений API Авито Реклама.

Используются строковые enum (наследники ``str, Enum``), поэтому значения можно
передавать как сам элемент перечисления, так и эквивалентную строку. Метод
:func:`BaseEnum.assert_valid` проверяет, что переданное значение допустимо.

Политика неизвестных значений: перечисления проверяют только **входные**
значения (роли пользователей, поля договора, тип юрлица). Поля ответов API
(статусы, ``budgetFrequency``, ``statusReasons`` и т. п.) модели возвращают
строкой как есть и не приводят к enum, поэтому новое значение, добавленное в
API, не вызывает ошибку. Сравнивайте их со значениями enum:
``campaign.status == CampaignStatus.ACTIVE``.
"""

from __future__ import annotations

from enum import Enum
from typing import List, Union

from .exceptions import ValidationError


class BaseEnum(str, Enum):
    """Базовый строковый enum с методами проверки значений."""

    @classmethod
    def values(cls) -> List[str]:
        """Возвращает список всех допустимых строковых значений."""
        return [member.value for member in cls]

    @classmethod
    def is_valid(cls, value: Union[str, "BaseEnum"]) -> bool:
        """Проверяет, входит ли значение в перечисление."""
        if isinstance(value, cls):
            return True
        return value in cls.values()

    @classmethod
    def assert_valid(cls, value: Union[str, "BaseEnum"]) -> str:
        """Проверяет значение и возвращает его строковое представление.

        :raises ValidationError: если значение недопустимо.
        """
        if isinstance(value, cls):
            return str(value.value)
        if value in cls.values():
            return str(value)
        raise ValidationError(
            f"Недопустимое значение '{value}' для {cls.__name__}. "
            f"Допустимые: {', '.join(cls.values())}."
        )


class LegalType(BaseEnum):
    """Тип юридического лица."""

    UL = "ul"
    IP = "ip"


class LegalRole(BaseEnum):
    """Роль контрагента в системе ОРД."""

    ADVERTISER = "rd"
    AGENCY = "ra"
    DISTRIBUTOR = "rr"


class UserRole(BaseEnum):
    """Роль пользователя в аккаунте."""

    ADMIN = "admin"
    VIEWER = "viewer"


class ContractType(BaseEnum):
    """Тип договора."""

    SERVICE = "service"
    INTERMEDIARY = "intermediary"
    EXTERNAL = "external"


class ContractSubject(BaseEnum):
    """Предмет договора."""

    ORG_DISTRIBUTION = "org-distribution"
    MEDIATION = "mediation"
    DISTRIBUTION = "distribution"
    REPRESENTATION = "representation"
    OTHER = "other"


class ContractAction(BaseEnum):
    """Действие по договору (поле ``object``)."""

    DISTRIBUTION = "distribution"
    CONCLUDE = "conclude"
    COMMERCIAL = "commercial"
    OTHER = "other"


class ContractCounterpartyType(BaseEnum):
    """Тип контрагента (поле ``description``)."""

    DIRECT_WITH_ADVERTISER = "direct_with_advertiser"
    ADVERTISER_INTERMEDIARY = "advertiser_intermediary"


class CampaignPaymentModel(BaseEnum):
    """Модель оплаты кампании."""

    CPM = "CPM"
    CPC = "CPC"


class CampaignType(BaseEnum):
    """Тип кампании."""

    TEXT_IMAGE = "textImage"
    HTML = "HTML"
    VIDEO = "video"


class CampaignStatus(BaseEnum):
    """Статус кампании."""

    DRAFT = "draft"
    IN_MODERATION = "in_moderation"
    MODERATION_FAILED = "moderation_failed"
    PARTIAL_MODERATION = "partial_moderation"
    ACTIVE = "active"
    WILL_LAUNCH_SOON = "will_launch_soon"
    PARTIALLY_ACTIVE = "partially_active"
    WILL_STOP_SOON = "will_stop_soon"
    PAUSING = "pausing"
    PAUSED = "paused"
    UNPAUSING = "unpausing"
    STOPPED = "stopped"
    FINISHED = "finished"
    ARCHIVED = "archived"


class GroupsStatus(BaseEnum):
    """Статус группы объявлений."""

    DRAFT = "draft"
    IN_MODERATION = "in_moderation"
    MODERATION_FAILED = "moderation_failed"
    WILL_LAUNCH_SOON = "will_launch_soon"
    ACTIVE = "active"
    WILL_STOP_SOON = "will_stop_soon"
    PAUSING = "pausing"
    PAUSED = "paused"
    UNPAUSING = "unpausing"
    STOPPED = "stopped"
    FINISHED = "finished"
    ARCHIVED = "archived"


class CreativesStatus(BaseEnum):
    """Статус креатива."""

    DRAFT = "draft"
    READY_FOR_MODERATION = "ready_for_moderation"
    IN_MODERATION = "in_moderation"
    MODERATION_FAILED = "moderation_failed"
    ERIR_REGISTRATION = "erir_registration"
    WILL_LAUNCH_SOON = "will_launch_soon"
    ACTIVE = "active"
    PAUSING = "pausing"
    PAUSED = "paused"
    UNPAUSING = "unpausing"
    STOPPED = "stopped"
    FINISHED = "finished"
    ARCHIVED = "archived"


class CampaignBudgetFrequency(BaseEnum):
    """Тип агрегата бюджета кампании (``Campaign.budgetFrequency``).

    ``mixed`` — в кампании есть группы и с дневным бюджетом, и с бюджетом на весь
    период; тогда ``budget``/``budgetKopeks`` у кампании отсутствуют.
    """

    DAILY = "daily"
    ENTIRE_PERIOD = "entirePeriod"
    MIXED = "mixed"


class BudgetFrequency(BaseEnum):
    """Частота расходования бюджета группы (``Group.budgetFrequency``)."""

    DAILY = "daily"
    ENTIRE_PERIOD = "entirePeriod"


class FrequencyPeriod(BaseEnum):
    """Период частотного ограничения (``FrequencyRule.period``)."""

    NO_LIMIT = "no_limit"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"


class GroupFormat(BaseEnum):
    """Формат группы объявлений."""

    MEDIA_ROOT = "mediaRoot"
    MEDIA_SELLER_PROFILE = "mediaSellerProfile"
    MEDIA_PREMIUM = "mediaPremium"
    MEDIA = "media"
    NATIVE = "native"
    HTML_PREMIUM = "htmlPremium"
    HTML = "html"
    VIDEO = "video"


class AudienceType(BaseEnum):
    """Тип аудитории таргетинга группы."""

    BASIC = "basic"
    READY = "ready"
    AUTOTARGETING = "autotargeting"


class Paces(BaseEnum):
    """Скорость показов группы."""

    ASAP = "asap"
    EVEN = "even"


class GroupPriceControl(BaseEnum):
    """Контроль цены группы."""

    MANUAL = "manual"
    AUTO = "auto"


class ScheduleType(BaseEnum):
    """Тип расписания показов группы."""

    ALWAYS = "always"
    WEEKDAYS_9_TO_20 = "weekdays9To20"
    CUSTOM = "custom"
