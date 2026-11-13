# Avito Ads Python SDK

[![CI](https://github.com/avito-tech/avito-ads-sdk-python3/actions/workflows/ci.yml/badge.svg)](https://github.com/avito-tech/avito-ads-sdk-python3/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Python SDK для API **Авито Реклама** (Avito Ads API).

- [Об Авито Реклама](http://avito.ru/ads)
- [Возможности API Авито Реклама](https://ads-help.avito.com/external/api)
- [Техническая документация API](https://developers.avito.ru/api-catalog/ads/documentation)

Библиотека закрывает все основные методы API: аккаунт и баланс, дочерние аккаунты и переводы средств, рекламодателей, договоры, кампании, группы объявлений, креативы, статистику и управление пользователями. Поддерживаются **два режима работы — синхронный и асинхронный** — с одинаковым набором методов. Транспорт построен на [httpx](https://www.python-httpx.org/), авторизация — OAuth2 `client_credentials` с автоматическим обновлением и кэшированием токена, а также повторными попытками при ошибках `429` и `5xx`.

## Версия SDK и API

Версия SDK = версия публичного API (swagger), под которую он собран. Текущая — **1.4.0**:

```python
import avito_ads

print(avito_ads.__version__)   # "1.4.0" — версия пакета
print(avito_ads.API_VERSION)   # "1.4.0" — версия swagger (info.version в openapi.json)
```

Спецификация лежит в корне репозитория (`openapi.json`); CI проверяет, что версия пакета,
`API_VERSION` и `info.version` совпадают.

## Возможности

- Поддержка **Python 3.8+**.
- **Синхронный (`Client`) и асинхронный (`AsyncClient`) режимы** с идентичным API — разница только в `await` / `async for` / `async with`.
- Установка в любой проект; интеграции с **Django**, **Flask**, **FastAPI** (асинхронная).
- OAuth2 `client_credentials`: автоматическое получение, кэширование и обновление токена.
- Раздельные окружения: **production** и **sandbox** (песочница).
- Автоматические повторы при `429`/`5xx` с экспоненциальной задержкой и учётом заголовка `Retry-After`; однократное обновление токена и повтор при `401`.
- Типизированные модели ответов и типизированные исключения по кодам ошибок.
- Постраничная выборка с удобным перебором всех страниц через генератор (`for`) или async-генератор (`async for`).
- Чтение остатка лимита из заголовка `Api-Point-Balance`.
- Полная типизация (`py.typed`, проверка `mypy --strict`).
- Документация и docstrings на русском языке.

## Требования

- Python >= 3.8
- `httpx >= 0.24, < 1.0`

## Установка

```bash
pip install avito-ads
```

С интеграциями:

```bash
pip install "avito-ads[flask]"     # или [django], [fastapi]
```

## Быстрый старт

```python
from avito_ads import Client, Configuration

config = Configuration.create(
    "ВАШ_CLIENT_ID",
    "ВАШ_CLIENT_SECRET",
    123456789,            # accountID — идентификатор рекламного аккаунта
).production()            # .sandbox() для песочницы

with Client(config) as client:
    # Баланс аккаунта (в рублях)
    balance = client.account.get_balance()
    print(balance.balance, "₽, бонусы:", balance.bonus_balance)
```

`accountID` — это идентификатор аккаунта, к которому привязан токен; он задаётся один раз в конфигурации и подставляется во все запросы автоматически.

## Синхронный и асинхронный режимы

Библиотека предоставляет два клиента с одинаковым набором ресурсов, методов и аргументов: синхронный `Client` и асинхронный `AsyncClient`. Оба создаются из одной и той же `Configuration`.

Синхронный режим:

```python
from avito_ads import Client, Configuration

config = Configuration.create("ID", "SECRET", 123456789).sandbox()
with Client(config) as client:
    balance = client.account.get_balance()
    for campaign in client.campaigns.iterate():
        print(campaign.id, campaign.name)
```

Асинхронный режим — те же вызовы с `await`, перебор через `async for`, клиент как `async with`:

```python
import asyncio
from avito_ads import AsyncClient, Configuration

async def main() -> None:
    config = Configuration.create("ID", "SECRET", 123456789).sandbox()
    async with AsyncClient(config) as client:
        balance = await client.account.get_balance()
        async for campaign in client.campaigns.iterate():
            print(campaign.id, campaign.name)

asyncio.run(main())
```

Оба клиента можно создавать и без менеджера контекста; в этом случае закрывайте их вручную: `client.close()` для синхронного и `await client.aclose()` для асинхронного.

## Конфигурация

Объект `Configuration` неизменяемый: все методы `with_*` и `production`/`sandbox` возвращают новый экземпляр.

```python
config = (
    Configuration.create(client_id, client_secret, account_id)
    .sandbox()                       # или .production()
    .with_timeout(30.0)              # таймаут запроса, сек
    .with_max_retries(4)             # макс. число повторов при 429/5xx
    .with_retry_base_delay(1000)     # базовая задержка повтора, мс
    .with_token_leeway(60)           # запас на досрочное обновление токена, сек
    .with_user_agent("my-app/1.0")   # свой User-Agent; метка SDK дописывается
)
```

При необходимости можно передать готовый HTTP-клиент httpx (например, с прокси, лимитами пула или HTTP/2):

```python
import httpx

# для синхронного Client
config = config.with_http_client(httpx.Client(http2=True))
# для асинхронного AsyncClient
config = config.with_async_client(httpx.AsyncClient(http2=True))
```

### User-Agent

По умолчанию SDK отправляет `User-Agent: avito-ads-sdk-python3/<версия>` — и в запросах к API, и в
запросе токена. По этой метке Авито видит, что запрос пришёл из Python SDK.

Свой `User-Agent` не заменяет метку, а дополняется ею через пробел:

```python
config = config.with_user_agent("my-app/1.0")
print(config.effective_user_agent)   # my-app/1.0 avito-ads-sdk-python3/1.4.0
```

Если в вашем значении метка `avito-ads-sdk-python3/` уже есть (без учёта регистра), второй раз она
не дописывается.

### Окружения

| Окружение | Базовый адрес API |
|---|---|
| `production()` | `https://api.avito.ru/ads/` |
| `sandbox()` | `https://api.avito.ru/ads-sandbox/` |

Эндпоинт получения токена общий для обоих окружений: `https://api.avito.ru/token`.

## Хранение и обновление токена

Токен запрашивается автоматически при первом обращении и переиспользуется до истечения срока. По умолчанию он хранится в памяти процесса. Чтобы переживать перезапуски, реализуйте свой класс хранилища и передайте его:

```python
# синхронный клиент — протокол avito_ads.auth.storage.TokenStorage (get/set/delete)
config = config.with_token_storage(my_storage)

# асинхронный клиент — протокол avito_ads.auth.storage.AsyncTokenStorage
# (async get/set/delete, удобно для асинхронного Redis)
config = config.with_async_token_storage(my_async_storage)
```

## Работа с методами API

Все группы методов доступны как свойства клиента.

### Аккаунт

```python
account = client.account.get()
print(account.short_name, "/ ИНН", account.inn)

balance = client.account.get_balance()
```

### Дочерние аккаунты и переводы

```python
for child in client.child_accounts.list():
    print(child.id, child.short_name)

# Создать дочерний аккаунт-непокупатель
created = client.child_accounts.create_nonpayer_child("ООО Дочка", True)

# Перевести средства / бонусы (сумма не менее 1)
client.child_accounts.transfer_funds(account_id_to=987654321, amount=5000)
client.child_accounts.transfer_bonus(account_id_to=987654321, amount=100)
```

### Рекламодатели

```python
from avito_ads.enums import LegalType, LegalRole

created = client.advertisers.create(
    inn="7712345678",
    short_name="ООО Реклама",
    long_name="Общество с ограниченной ответственностью «Реклама»",
    ogrn="1177746123456",
    legal_address="г. Москва, ул. Примерная, д. 1",
    actual_address="г. Москва, ул. Примерная, д. 1",
    legal_role=LegalRole.ADVERTISER,
    legal_type=LegalType.UL,
    kpp="771701001",
)

advertisers = client.advertisers.list()
```

### Договоры

Для создания договора удобно использовать `ContractBuilder` — он проверяет обязательные поля по типу договора и бросает понятное исключение валидации ещё до запроса.

```python
from avito_ads import ContractBuilder
from avito_ads.enums import ContractCounterpartyType

builder = (
    ContractBuilder.intermediary_contract()
    .advertiser(987654321)
    .counterparty_type(ContractCounterpartyType.DIRECT_WITH_ADVERTISER)
    .subject("mediation")
    .object("commercial")
    .reporting_required(True)
    .funds_allocation_to_principal(False)
    .date("2025-01-15")
    .number("ДА-2025/01")
    .intermediary({
        "shortName": "ООО Реклама",
        "longName": "Общество с ограниченной ответственностью «Реклама»",
        "inn": "7712345678",
        "ogrn": "1177746123456",
        "kpp": "771701001",
        "legalAddress": "г. Москва, ул. Примерная, д. 1",
        "actualAddress": "г. Москва, ул. Примерная, д. 1",
        "legalType": "ul",
    })
)

created = client.contracts.create(builder)
print("ID договора:", created.id)
```

Доступны быстрые конструкторы `ContractBuilder.service()`, `ContractBuilder.intermediary_contract()` и `ContractBuilder.external("CID")`. Дополнительное соглашение создаётся вызовом `.parent_id(...)` (поле `intermediary` при этом передавать нельзя).

В `create()` можно передать и готовый словарь тела запроса — тогда клиентская валидация не выполняется.

```python
contracts = client.contracts.list()
```

### Кампании, группы, креативы

```python
for campaign in client.campaigns.list():
    print(campaign.id, campaign.name, f"[{campaign.status}]")

groups = client.groups.list()
creatives = client.creatives.list()

# Изменение бюджета и ставки группы (только ручное управление ставкой; значение не менее 1)
client.groups.change_budget(group_id=555, budget=100000)
client.groups.change_price(group_id=555, price=25)
```

#### Причины статуса

У кампании, группы и креатива есть `status_reasons` — все коды причин текущего статуса (`[]`, если
причин нет) и `top_status_reason` — главная причина (`""`, если не определена). API может добавлять
новые коды, поэтому обрабатывайте неизвестные значения:

```python
from avito_ads import CampaignStatus

for campaign in client.campaigns.iterate():
    if campaign.status == CampaignStatus.PAUSED and campaign.top_status_reason:
        print(campaign.id, "на паузе:", campaign.top_status_reason, campaign.status_reasons)
```

Статусы, `budget_frequency` и другие значения перечислений модели возвращают **строкой как есть**:
новое значение, появившееся в API, не вызывает ошибку. Перечисления из `avito_ads.enums` нужны для
сравнения и для проверки входных значений.

#### Бюджет кампании (может отсутствовать)

`Campaign.budget` и `budget_kopeks` — сумма бюджетов групп, `Optional[int]`. Если в кампании есть
группы и с дневным бюджетом, и с бюджетом на весь период (`budget_frequency == "mixed"`), бюджета
нет и поле равно `None`; у пустой кампании — `0`. Не подменяйте `None` нулём:

```python
from avito_ads import CampaignBudgetFrequency

if campaign.budget_kopeks is None:
    print("Бюджет не суммируется:", campaign.budget_frequency)   # mixed
else:
    print("Бюджет:", campaign.budget_kopeks / 100, "₽")
```

Денежные поля в копейках есть также у баланса (`balance_kopeks`, `bonus_balance_kopeks`),
статистики (`spend_kopeks`, `spend_bonus_kopeks`) и группы (`budget_kopeks`, `price_kopeks`).

#### Частотные ограничения группы

```python
for group in client.groups.iterate():
    for rule in group.frequency_rules:   # FrequencyRule: count показов за period
        print(group.id, rule.count, rule.period)   # period: no_limit / day / week / month
```

`Group.frequency_count`/`frequency_period` оставлены для совместимости (соответствуют первому
правилу) и помечены устаревшими: при чтении выдаётся `DeprecationWarning`. Так же помечен
`Creative.legal_info` — используйте `Creative.kktu_fields`.

#### Конфликт при изменении группы (409)

Если группу изменили параллельно, `change_budget`/`change_price` бросают `ConflictError`
(наследник `ApiError`). Перечитайте группу и повторите изменение:

```python
from avito_ads.exceptions import ConflictError

try:
    client.groups.change_budget(group_id=555, budget=100000)
except ConflictError:
    ...  # перечитать группу и повторить
```

### Статистика

Период не может превышать 100 дней; даты — в формате `YYYY-MM-DD`. Эти ограничения проверяются на стороне клиента.

```python
stats = client.statistics.campaign(campaign_id=555, date_from="2025-01-01", date_to="2025-01-31")
total = stats.campaign.total_data
print("Показы:", total.views, "клики:", total.clicks)

by_groups = client.statistics.groups(555, "2025-01-01", "2025-01-31", [101, 102])
by_creatives = client.statistics.creatives(555, "2025-01-01", "2025-01-31", [201, 202])
```

### Пользователи

```python
from avito_ads.enums import UserRole

users = client.users.list()
client.users.add(user_id=42, role=UserRole.ADMIN)
client.users.set_role(user_id=42, role=UserRole.VIEWER)
client.users.delete(user_id=42)
```

## Постраничная выборка

Методы `list()` возвращают `PaginatedResult` — по нему можно итерироваться и брать `len()`.

```python
result = client.campaigns.list(limit=50, page=1)

print("Всего:", result.total)
print("Остаток лимита API:", result.api_point_balance)

for campaign in result:
    ...

if result.has_next_page():
    next_page = client.campaigns.list(limit=50, page=2)
```

Чтобы обойти все страницы автоматически, используйте `iterate()` — он возвращает генератор и подгружает страницы по мере необходимости:

```python
for campaign in client.campaigns.iterate():
    print(campaign.name)
```

В асинхронном режиме `iterate()` возвращает async-генератор:

```python
async for campaign in async_client.campaigns.iterate():
    print(campaign.name)
```

## Фильтры

Фильтры можно задавать словарём или объектом-фильтром с проверкой имён полей.

```python
from avito_ads import CampaignsFilter, DateRange
from avito_ads.enums import CampaignStatus

f = (
    CampaignsFilter()
    .statuses([CampaignStatus.ACTIVE.value, CampaignStatus.WILL_STOP_SOON.value])
    .contract_ids([10, 20])
    .created_at(DateRange("2025-01-01", "2025-01-31"))
)

campaigns = client.campaigns.list(f)
```

Значения `statuses` передаются в API без проверки на клиенте — доступны все статусы swagger 1.4.0,
включая `will_launch_soon`, `partially_active`, `will_stop_soon`, `pausing`, `unpausing`.

Пустой фильтр корректно сериализуется в JSON-объект `{}`, как того требует API.

## Обработка ошибок

Все исключения наследуются от `avito_ads.exceptions.AvitoAdsError`.

| HTTP | Исключение |
|---|---|
| 400 | `BadRequestError` |
| 401 | `AuthenticationError` |
| 403 | `AccessDeniedError` |
| 404 | `NotFoundError` |
| 409 | `ConflictError` (конфликт версий группы в `change_budget`/`change_price`) |
| 429 | `RateLimitError` (атрибут `retry_after`) |
| 5xx | `ServerError` |
| сеть/таймаут | `NetworkError` |

```python
from avito_ads.exceptions import ApiError, RateLimitError

try:
    client.account.get_balance()
except RateLimitError as exc:
    retry_after = exc.retry_after
except ApiError as exc:
    print(exc.status_code, exc.error_code, str(exc))
```

Ошибки валидации на стороне клиента (неверный период статистики, сумма перевода меньше 1, неизвестная роль и т. п.) бросают `avito_ads.exceptions.ValidationError`.

## Лимиты и повторы

API ограничивает частоту запросов (порядка 500 в минуту). Клиент автоматически повторяет запросы при `429` и `5xx` с экспоненциальной задержкой и учитывает заголовок `Retry-After`. Остаток лимита доступен из заголовка `Api-Point-Balance` (например, `PaginatedResult.api_point_balance`).

## Интеграция с Django

В `settings.py`:

```python
AVITO_ADS = {
    "client_id": "...",
    "client_secret": "...",
    "account_id": 123456789,
    "environment": "production",
}
```

Использование:

```python
from avito_ads.integrations.django import get_client

balance = get_client().account.get_balance()
```

Опционально добавьте `"avito_ads.integrations.django"` в `INSTALLED_APPS`, чтобы конфигурация проверялась при старте приложения.

## Интеграция с Flask

```python
from flask import Flask
from avito_ads.integrations.flask import AvitoAds

app = Flask(__name__)
app.config.update(
    AVITO_ADS_CLIENT_ID="...",
    AVITO_ADS_CLIENT_SECRET="...",
    AVITO_ADS_ACCOUNT_ID=123456789,
    AVITO_ADS_ENVIRONMENT="production",
)

avito = AvitoAds(app)

@app.route("/balance")
def balance():
    return {"balance": avito.client.account.get_balance().balance}
```

Поддерживается и фабричный паттерн через `AvitoAds().init_app(app)`.

## Интеграция с FastAPI

FastAPI — асинхронный фреймворк, поэтому интеграция отдаёт асинхронный `AsyncClient`:

```python
from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI
from avito_ads import AsyncClient
from avito_ads.integrations.fastapi import AvitoAdsProvider

avito = AvitoAdsProvider({
    "client_id": "...",
    "client_secret": "...",
    "account_id": 123456789,
    "environment": "production",
})

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await avito.aclose()

app = FastAPI(lifespan=lifespan)

@app.get("/balance")
async def balance(client: AsyncClient = Depends(avito)):
    result = await client.account.get_balance()
    return {"balance": result.balance}
```

## Песочница

Создание тестового аккаунта доступно только в песочнице:

```python
from avito_ads.enums import LegalType

config = Configuration.create(client_id, client_secret, account_id).sandbox()

with Client(config) as client:
    created = client.account.create_sandbox_account(
        inn="7712345678",
        short_name="Тестовый аккаунт",
        long_name="Полное наименование",
        ogrn="1177746123456",
        legal_address="г. Москва, ул. Примерная, д. 1",
        actual_address=None,              # None — возьмётся юридический адрес
        contact={"name": "Иван Иванов", "phone": "+79001234567"},
        legal_type=LegalType.UL,          # обязателен: "ul" или "ip"
    )
    print(created.account_id)
    for warning in created.warnings:     # ответ 207: аккаунт создан, но не всё подготовлено
        print("Предупреждение:", warning)
```

Ответ `207` считается успехом: аккаунт создан, а что не подготовилось — в `created.warnings`
(пустой список — аккаунт подготовлен полностью).

## Разработка и тестирование

```bash
pip install -e ".[dev]"
pytest            # модульные тесты
ruff check .      # линтер
mypy avito_ads    # проверка типов (strict)
```

Интеграционные тесты против реальной песочницы по умолчанию пропускаются. Чтобы запустить их:

```bash
AVITO_ADS_RUN_INTEGRATION=1 \
AVITO_ADS_CLIENT_ID=... \
AVITO_ADS_CLIENT_SECRET=... \
AVITO_ADS_ACCOUNT_ID=... \
pytest -m integration
```

## Лицензия

[MIT](LICENSE).
