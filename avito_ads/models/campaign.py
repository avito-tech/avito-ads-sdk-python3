"""Модель рекламной кампании."""

from __future__ import annotations

from typing import Optional

from .base import Model


class Campaign(Model):
    """Рекламная кампания."""

    @property
    def id(self) -> Optional[int]:
        return self._int("id")

    @property
    def name(self) -> Optional[str]:
        return self._str("name")

    @property
    def status(self) -> Optional[str]:
        return self._str("status")

    @property
    def budget(self) -> Optional[int]:
        return self._int("budget")

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
    def created_at(self) -> Optional[str]:
        return self._str("createdAt")

    @property
    def updated_at(self) -> Optional[str]:
        return self._str("updatedAt")
