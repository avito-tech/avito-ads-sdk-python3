"""Конструктор тела запроса для создания договора.

Инкапсулирует правила обязательности полей по типу договора и проверяет их до
отправки, чтобы вместо ответа 400 от API вернуть понятную ошибку валидации.

Правила по типу:

* ``service``      — обязательны ``subject``, ``isReportingRequired``, ``date``,
  ``number``; запрещён ``cid``.
* ``intermediary`` — обязательны ``subject``, ``object``, ``isReportingRequired``,
  ``isFundsAllocationToPrincipal``, ``date``, ``number``; запрещён ``cid``.
* ``external``     — обязателен ``cid``; запрещён ``parentId``; ``date``/``number``
  необязательны.

Поле ``intermediary`` (данные исполнителя) обязательно, если не задан
``parentId``, и недопустимо, если ``parentId`` задан (доп. соглашение).
"""

from __future__ import annotations

from typing import Any, Dict, Union

from .enums import (
    ContractAction,
    ContractCounterpartyType,
    ContractSubject,
    ContractType,
)
from .exceptions import ValidationError


class ContractBuilder:
    """Билдер договора с проверкой правил по типу."""

    def __init__(self) -> None:
        self._data: Dict[str, Any] = {}

    # --- Фабрики -------------------------------------------------------------

    @classmethod
    def create(cls) -> "ContractBuilder":
        return cls()

    @classmethod
    def service(cls) -> "ContractBuilder":
        """Договор на оказание услуг."""
        return cls().type(ContractType.SERVICE)

    @classmethod
    def intermediary_contract(cls) -> "ContractBuilder":
        """Посреднический договор."""
        return cls().type(ContractType.INTERMEDIARY)

    @classmethod
    def external(cls, cid: str) -> "ContractBuilder":
        """Внешний договор."""
        return cls().type(ContractType.EXTERNAL).cid(cid)

    # --- Поля ----------------------------------------------------------------

    def advertiser(self, advertiser_id: int) -> "ContractBuilder":
        self._data["advertiserId"] = advertiser_id
        return self

    def type(self, contract_type: Union[str, ContractType]) -> "ContractBuilder":
        self._data["type"] = ContractType.assert_valid(contract_type)
        return self

    def counterparty_type(
        self, counterparty_type: Union[str, ContractCounterpartyType]
    ) -> "ContractBuilder":
        """Тип контрагента (поле API ``description``)."""
        self._data["description"] = ContractCounterpartyType.assert_valid(counterparty_type)
        return self

    def subject(self, subject: Union[str, ContractSubject]) -> "ContractBuilder":
        self._data["subject"] = ContractSubject.assert_valid(subject)
        return self

    def object(self, action: Union[str, ContractAction]) -> "ContractBuilder":
        self._data["object"] = ContractAction.assert_valid(action)
        return self

    def cid(self, cid: str) -> "ContractBuilder":
        self._data["cid"] = cid
        return self

    def date(self, date: str) -> "ContractBuilder":
        """Дата в формате ``YYYY-MM-DD``."""
        self._data["date"] = date
        return self

    def number(self, number: str) -> "ContractBuilder":
        self._data["number"] = number
        return self

    def reporting_required(self, value: bool) -> "ContractBuilder":
        self._data["isReportingRequired"] = value
        return self

    def funds_allocation_to_principal(self, value: bool) -> "ContractBuilder":
        self._data["isFundsAllocationToPrincipal"] = value
        return self

    def parent_id(self, parent_id: int) -> "ContractBuilder":
        self._data["parentId"] = parent_id
        return self

    def intermediary(self, intermediary: Dict[str, Any]) -> "ContractBuilder":
        """Данные исполнителя (посредника)."""
        self._data["intermediary"] = intermediary
        return self

    # --- Сборка --------------------------------------------------------------

    def build(self) -> Dict[str, Any]:
        """Проверяет и собирает тело запроса.

        :raises ValidationError: при нарушении правил по типу договора.
        """
        self._require("advertiserId", "Не задан advertiserId.")
        self._require("type", "Не задан type договора.")
        self._require("description", "Не задан тип контрагента (counterparty_type).")

        contract_type = self._data["type"]
        has_parent = "parentId" in self._data

        if contract_type == ContractType.EXTERNAL.value:
            self._require("cid", "Для внешнего договора (external) обязателен cid.")
            if has_parent:
                raise ValidationError(
                    "Для внешнего договора (external) нельзя передавать parentId."
                )

        if contract_type in (ContractType.SERVICE.value, ContractType.INTERMEDIARY.value):
            self._require("subject", f"Для договора типа {contract_type} обязателен subject.")
            self._require(
                "isReportingRequired",
                f"Для договора типа {contract_type} обязателен isReportingRequired.",
            )
            self._require("date", f"Для договора типа {contract_type} обязательны date и number.")
            self._require("number", f"Для договора типа {contract_type} обязательны date и number.")
            if "cid" in self._data:
                raise ValidationError(
                    f"Для договора типа {contract_type} нельзя передавать cid."
                )

        if contract_type == ContractType.INTERMEDIARY.value:
            self._require("object", "Для посреднического договора обязателен object.")
            self._require(
                "isFundsAllocationToPrincipal",
                "Для посреднического договора обязателен isFundsAllocationToPrincipal.",
            )

        has_intermediary = "intermediary" in self._data
        if has_parent and has_intermediary:
            raise ValidationError(
                "Для доп. соглашения (задан parentId) нельзя передавать intermediary."
            )
        if not has_parent and not has_intermediary:
            raise ValidationError(
                "Не задан parentId — необходимо передать данные исполнителя (intermediary)."
            )

        return dict(self._data)

    def _require(self, key: str, message: str) -> None:
        if key not in self._data:
            raise ValidationError(message)
