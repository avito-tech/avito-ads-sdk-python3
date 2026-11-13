"""Модель креатива."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from .base import Model, warn_deprecated


class KKTUFieldValue(Model):
    """Заполненное поле динамической формы ККТУ (элемент ``kktuFields``)."""

    @property
    def key(self) -> Optional[str]:
        """Внутренний ключ поля."""
        return self._str("key")

    @property
    def value(self) -> Optional[str]:
        """Значение поля, приведённое к строке."""
        return self._str("value")


class Creative(Model):
    """Креатив.

    ``status``, ``status_reasons`` и ``top_status_reason`` возвращаются строками
    как есть: новые значения, добавленные в API, не вызывают ошибку.
    """

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
        """Статус креатива (см. :class:`~avito_ads.enums.CreativesStatus`)."""
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
    def user_id(self) -> Optional[int]:
        """ID пользователя, создавшего креатив (``userID``)."""
        return self._int("userID")

    @property
    def landing_id(self) -> Optional[int]:
        """ID посадочной страницы (``landingID``)."""
        return self._int("landingID")

    @property
    def origin_url(self) -> Optional[str]:
        """Оригинальная ссылка для аналитики (``originUrl``)."""
        return self._str("originUrl")

    @property
    def preview_url(self) -> Optional[str]:
        """Ссылка на предпросмотр креатива (``previewUrl``)."""
        return self._str("previewUrl")

    @property
    def kktu_fields(self) -> List[KKTUFieldValue]:
        """Заполненные поля динамической формы ККТУ (``kktuFields``)."""
        return self._models("kktuFields", KKTUFieldValue)

    @property
    def legal_info(self) -> Dict[str, Any]:
        """Устаревшее представление юридических данных.

        .. deprecated:: 1.2.0
            Используйте :attr:`kktu_fields`. Поле остаётся для совместимости.
        """
        warn_deprecated("Creative.legal_info", "используйте Creative.kktu_fields.")
        return self._dict("legalInfo")
