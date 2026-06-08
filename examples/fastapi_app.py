"""Пример интеграции с FastAPI (асинхронный режим).

Запуск:
    pip install avito-ads[fastapi] uvicorn
    AVITO_ADS_CLIENT_ID=... AVITO_ADS_CLIENT_SECRET=... AVITO_ADS_ACCOUNT_ID=... \
    uvicorn examples.fastapi_app:app
"""

from __future__ import annotations

import os
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import Depends, FastAPI

from avito_ads import AsyncClient
from avito_ads.integrations.fastapi import AvitoAdsProvider

avito = AvitoAdsProvider(
    {
        "client_id": os.environ.get("AVITO_ADS_CLIENT_ID", ""),
        "client_secret": os.environ.get("AVITO_ADS_CLIENT_SECRET", ""),
        "account_id": int(os.environ.get("AVITO_ADS_ACCOUNT_ID", "0")),
        "environment": os.environ.get("AVITO_ADS_ENVIRONMENT", "sandbox"),
    }
)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    yield
    await avito.aclose()


app = FastAPI(lifespan=lifespan)


@app.get("/balance")
async def balance(client: AsyncClient = Depends(avito)) -> dict:  # noqa: B008
    result = await client.account.get_balance()
    return {"balance": result.balance, "bonus": result.bonus_balance}
