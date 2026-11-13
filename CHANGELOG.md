# Changelog

Все заметные изменения в этом проекте документируются в этом файле.

Формат основан на [Keep a Changelog](https://keepachangelog.com/ru/1.0.0/),
проект придерживается [семантического версионирования](https://semver.org/lang/ru/).

## [1.4.0] — 2026-11-13

Синхронизация с публичным swagger 1.4.0. С этой версии **версия SDK = версия публичного API (swagger)**.

### Breaking
- Пользовательский User-Agent теперь дополняется меткой SDK, а не заменяет её:
  `with_user_agent("my-app/1.0")` даёт `my-app/1.0 avito-ads-sdk-python3/1.4.0`. Метка по
  умолчанию сменилась с `avito-ads-python/0.1.0` на `avito-ads-sdk-python3/<версия>`.
- `account.create_sandbox_account`: `legal_type` (`"ul"`/`"ip"`) обязателен по swagger — без него
  или с неизвестным значением бросается `ValidationError` до запроса.
- Изменения swagger, ломающие клиентов API: значение `weekly` у `budgetFrequency` группы удалено;
  входные `frequencyCount`/`frequencyPeriod` при создании группы заменены на `frequencyRules`
  (метода создания группы в SDK нет, в ответе группы старые поля сохранены).

### Added
- Константы `avito_ads.API_VERSION` (`"1.4.0"`), `avito_ads.__version__`, `avito_ads.DEFAULT_USER_AGENT`;
  `Configuration.effective_user_agent`. `openapi.json` (swagger 1.4.0) в корне репозитория, проверка в CI:
  версия пакета == `info.version` == `API_VERSION`.
- `ConflictError` (HTTP 409, наследник `ApiError`) — конфликт версий группы в `groups.change_budget` и
  `groups.change_price`.
- Денежные поля в копейках: `Balance.balance_kopeks`, `bonus_balance_kopeks`; `StatsData.spend_kopeks`,
  `spend_bonus_kopeks`; `Campaign.budget_kopeks`; `Group.budget_kopeks`, `price_kopeks`.
- Кампания: `budget_frequency` (`daily`/`entirePeriod`/`mixed`), `performance_additional_agreement_id`.
- `status_reasons` (список кодов, `[]` без причин) и `top_status_reason` (`""` без причины) у кампании,
  группы и креатива.
- Статусы кампании `will_launch_soon`, `partially_active`, `will_stop_soon`, `pausing`, `unpausing`;
  статусы креатива `will_launch_soon`, `pausing`, `unpausing`.
- Группа: `frequency_rules` (`FrequencyRule.count`/`period`), `budget_frequency`, `actions`,
  `activity_schedule`, `audience_type`, `format`, `pace`, `period_start_at`, `period_end_at`,
  `period_timezone`, `price_control`, `schedule_type`, `start_asap`, `user_id`, `targeting_*_ids` (8 полей).
- Креатив: `kktu_fields` (`KKTUFieldValue.key`/`value`), `landing_id`, `origin_url`, `preview_url`, `user_id`.
- Договор: `is_agent_acting_for_publisher`, `is_creative_reporter`.
- Sandbox: `CreatedAccount.warnings`; ответ `207` (аккаунт создан частично) — успех.
- Перечисления `CampaignBudgetFrequency`, `BudgetFrequency`, `FrequencyPeriod`, `GroupFormat`,
  `AudienceType`, `Paces`, `GroupPriceControl`, `ScheduleType`.
- Типы статистики `CampaignStatistic`, `GroupStatistic`, `CreativeStatistic` (наследники `EntityStatistic`).

### Changed
- Явная политика неизвестных значений: статусы, `budget_frequency`, коды причин и прочие значения
  перечислений в ответах возвращаются строками как есть; enum проверяются только на входе.
- `statistics.groups()`/`creatives()` возвращают `GroupStatistic`/`CreativeStatistic`,
  `CampaignStatisticResult.campaign` — `CampaignStatistic`.
- `Campaign.budget`/`budget_kopeks` по swagger nullable: тип `Optional[int]` прежний, теперь задокументировано,
  что `None` у mixed-кампании (бюджета нет) не равен `0` у пустой кампании.
- `create_sandbox_account`: `actual_address` может быть `None` (API возьмёт юридический адрес).
- Исправлена ошибка mypy в `auth/storage.py` (импорт `Protocol` напрямую из `typing`).

### Deprecated
- `Creative.legal_info` — используйте `kktu_fields` (swagger 1.2.0).
- `Group.frequency_count`/`frequency_period` — используйте `frequency_rules`.
- `EntityStatistic.payment_model`/`campaign_type` (только у `CampaignStatistic`) и
  `EntityStatistic.group_id` (только у `CreativeStatistic`).

Устаревшие поля не удалены: при чтении выдаётся `DeprecationWarning`.

## [0.1.0]

### Added
- Python SDK для API Авито Реклама в **двух режимах работы**: синхронном
  (`Client`) и асинхронном (`AsyncClient`) с идентичным набором методов.
- Ресурсы: аккаунт и баланс, дочерние аккаунты и переводы средств/бонусов,
  рекламодатели, договоры (с `ContractBuilder`), кампании, группы, креативы,
  статистика, пользователи.
- OAuth2 `client_credentials` с кэшированием и автоматическим обновлением токена
  (синхронное и асинхронное хранилища токена).
- Окружения production и sandbox.
- Автоматические повторы при `429`/`5xx` и обновление токена при `401`.
- Типизированные модели и исключения; полная типизация (`py.typed`,
  `mypy --strict`).
- Постраничная выборка и обход всех страниц через `iterate()` (генератор) и
  `async for` (async-генератор).
- Менеджеры контекста: `with Client(...)` и `async with AsyncClient(...)`.
- Интеграции с Django, Flask и (асинхронная) FastAPI.
- Тесты на `pytest` + `pytest-asyncio`, параметризованные для обоих режимов
  (HTTP мокируется через `httpx.MockTransport`, без сети); опциональные
  интеграционные тесты против песочницы.

### Notes
- Единый транспорт — [httpx](https://www.python-httpx.org/) (sync + async).
  Общая «sans-I/O» логика (операции, разбор ответов, политика повторов)
  переиспользуется обоими режимами, что исключает их расхождение.
