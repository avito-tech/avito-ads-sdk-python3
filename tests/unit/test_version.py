"""Версия SDK совпадает с версией swagger в openapi.json."""

from __future__ import annotations

import json
from pathlib import Path

import avito_ads

OPENAPI = Path(__file__).resolve().parents[2] / "openapi.json"


def test_versions_match_openapi():
    spec_version = json.loads(OPENAPI.read_text(encoding="utf-8"))["info"]["version"]
    assert spec_version == avito_ads.API_VERSION
    assert avito_ads.__version__ == spec_version
