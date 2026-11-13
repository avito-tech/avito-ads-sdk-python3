"""Версия SDK, версия публичного API и сборка заголовка ``User-Agent``.

Единственный источник версии пакета: ``pyproject.toml`` читает ``__version__``
отсюда (``[tool.setuptools.dynamic]``), из неё же собирается ``User-Agent``.
Версия SDK совпадает с версией публичного API (swagger), под которую он собран.
"""

from __future__ import annotations

from typing import Optional

__version__ = "1.4.0"

#: Версия публичного API Авито Реклама (``info.version`` в swagger), под которую собран SDK.
API_VERSION = "1.4.0"

#: Метка SDK в ``User-Agent``; по ней сервер определяет, что запрос пришёл из Python SDK.
USER_AGENT_PRODUCT = "avito-ads-sdk-python3"

#: ``User-Agent`` по умолчанию: ``avito-ads-sdk-python3/<версия>``.
DEFAULT_USER_AGENT = f"{USER_AGENT_PRODUCT}/{__version__}"


def build_user_agent(user_agent: Optional[str] = None) -> str:
    """Собирает итоговое значение заголовка ``User-Agent``.

    Пользовательский ``User-Agent`` не заменяет метку SDK, а дополняется ею через
    пробел: ``my-app/1.0 avito-ads-sdk-python3/1.4.0``. Если метка
    ``avito-ads-sdk-python3/`` уже есть (без учёта регистра), второй раз она не
    дописывается. Пустое значение даёт ``User-Agent`` по умолчанию.
    """
    custom = (user_agent or "").strip()
    if not custom:
        return DEFAULT_USER_AGENT
    if f"{USER_AGENT_PRODUCT}/" in custom.lower():
        return custom
    return f"{custom} {DEFAULT_USER_AGENT}"
