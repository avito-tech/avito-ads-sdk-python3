"""Создание посреднического договора через ContractBuilder и вывод списка."""

from __future__ import annotations

import os

from avito_ads import Client, Configuration, ContractBuilder
from avito_ads.enums import ContractCounterpartyType
from avito_ads.exceptions import ValidationError


def main() -> None:
    client = Client(
        Configuration.create(
            os.environ["AVITO_ADS_CLIENT_ID"],
            os.environ["AVITO_ADS_CLIENT_SECRET"],
            int(os.environ["AVITO_ADS_ACCOUNT_ID"]),
        ).sandbox()
    )

    try:
        builder = (
            ContractBuilder.intermediary_contract()
            .advertiser(int(os.environ.get("AVITO_ADS_ADVERTISER_ID", "0")))
            .counterparty_type(ContractCounterpartyType.DIRECT_WITH_ADVERTISER)
            .subject("mediation")
            .object("commercial")
            .reporting_required(True)
            .funds_allocation_to_principal(False)
            .date("2025-01-15")
            .number("ДА-2025/01")
            .intermediary(
                {
                    "shortName": "ООО Реклама",
                    "longName": "Общество с ограниченной ответственностью «Реклама»",
                    "inn": "7712345678",
                    "ogrn": "1177746123456",
                    "kpp": "771701001",
                    "legalAddress": "г. Москва, ул. Примерная, д. 1",
                    "actualAddress": "г. Москва, ул. Примерная, д. 1",
                    "legalType": "ul",
                }
            )
        )
        created = client.contracts.create(builder)
        print(f"Создан договор ID: {created.id}")
    except ValidationError as exc:
        print(f"Договор не прошёл валидацию: {exc}")

    for contract in client.contracts.iterate():
        print(f"{contract.id} {contract.number} [{contract.type}]")


if __name__ == "__main__":
    main()
