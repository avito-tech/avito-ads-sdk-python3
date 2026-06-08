"""Модель креатива."""

from __future__ import annotations

from typing import Any, Dict, Optional

from .base import Model


class Creative(Model):
    """Креатив."""

    @property
    def id(self) -> Optional[int]:
        return self._int("id")

    @property
    def name(self) -> Optional[str]:
        return self._str("name")

    @property
    def title(self) -> Optional[str]:
        return self._str("title")

    @property
    def description(self) -> Optional[str]:
        return self._str("description")

    @property
    def button_text(self) -> Optional[str]:
        return self._str("buttonText")

    @property
    def link(self) -> Optional[str]:
        return self._str("link")

    @property
    def status(self) -> Optional[str]:
        return self._str("status")

    @property
    def group_id(self) -> Optional[int]:
        return self._int("groupID")

    @property
    def campaign_id(self) -> Optional[int]:
        return self._int("campaignID")

    @property
    def account_id(self) -> Optional[int]:
        return self._int("accountID")

    @property
    def advertiser_id(self) -> Optional[int]:
        return self._int("advertiserID")

    @property
    def manager_id(self) -> Optional[int]:
        return self._int("managerID")

    @property
    def payment_model(self) -> Optional[str]:
        return self._str("paymentModel")

    @property
    def campaign_type(self) -> Optional[str]:
        return self._str("campaignType")

    @property
    def legal_info(self) -> Dict[str, Any]:
        return self._dict("legalInfo")
