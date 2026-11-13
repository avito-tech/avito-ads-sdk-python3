"""Модель рекламной кампании."""

from __future__ import annotations

from typing import List, Optional

from .base import Model


class Campaign(Model):
    """Рекламная кампания.

    Значения ``status``, ``budget_frequency``, ``status_reasons`` и
    ``top_status_reason`` возвращаются строками как есть: новые значения,
    добавленные в API, не вызывают ошибку. Известные значения — в
    :class:`~avito_ads.enums.CampaignStatus` и
    :class:`~avito_ads.enums.CampaignBudgetFrequency`.
    """

    @property
    def id(self) -> Optional[int]:
        return self._int("id")

    @property
    def name(self) -> Optional[str]:
        return self._str("name")

    @property
    def status(self) -> Optional[str]:
        """Статус кампании (см. :class:`~avito_ads.enums.CampaignStatus`)."""
        return self._str("status")

    @property
    def status_reasons(self) -> List[str]:
        """Все коды причин текущего статуса (``[]``, если причин нет).

        Порядок не отражает приоритет; возможны новые коды.
        """
        return self._str_list("statusReasons")

    @property
    def top_status_reason(self) -> str:
        """Главная причина текущего статуса (``""``, если не определена)."""
        return self._str("topStatusReason") or ""

    @property
    def budget(self) -> Optional[int]:
        """Сумма бюджетов групп в целых рублях с НДС.

        ``None`` — бюджета нет (``budget_frequency == "mixed"``: в кампании есть
        группы и с дневным бюджетом, и с бюджетом на весь период). У пустой
        кампании — ``0``. Не подменяйте ``None`` нулём.
        """
        return self._int("budget")

    @property
    def budget_kopeks(self) -> Optional[int]:
        """Точная сумма бюджетов групп в копейках с НДС; ``None`` — как у :attr:`budget`."""
        return self._int("budgetKopeks")

    @property
    def budget_frequency(self) -> Optional[str]:
        """Тип агрегата бюджета: ``daily``, ``entirePeriod`` или ``mixed``.

        См. :class:`~avito_ads.enums.CampaignBudgetFrequency`.
        """
        return self._str("budgetFrequency")

    @property
    def payment_model(self) -> Optional[str]:
        return self._str("paymentModel")

    @property
    def campaign_type(self) -> Optional[str]:
        return self._str("campaignType")

    @property
    def start_date(self) -> Optional[str]:
        return self._str("startDate")

    @property
    def end_date(self) -> Optional[str]:
        return self._str("endDate")

    @property
    def user_id(self) -> Optional[int]:
        return self._int("userId")

    @property
    def account_id(self) -> Optional[int]:
        return self._int("accountId")

    @property
    def advertiser_id(self) -> Optional[int]:
        return self._int("advertiserId")

    @property
    def contract_id(self) -> Optional[int]:
        return self._int("contractId")

    @property
    def manager_id(self) -> Optional[int]:
        return self._int("managerID")

    @property
    def additional_agreement_id(self) -> Optional[int]:
        return self._int("additionalAgreementID")

    @property
    def performance_additional_agreement_id(self) -> Optional[int]:
        """ID доп. соглашения к исполнительскому договору (``performanceAdditionalAgreementID``)."""
        return self._int("performanceAdditionalAgreementID")

    @property
    def created_at(self) -> Optional[str]:
        return self._str("createdAt")

    @property
    def updated_at(self) -> Optional[str]:
        return self._str("updatedAt")
