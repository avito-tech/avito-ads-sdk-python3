"""Тесты модели токена."""

from __future__ import annotations

from avito_ads.auth.token import AccessToken


def test_from_response_computes_expiry():
    token = AccessToken.from_response(
        {"access_token": "abc", "expires_in": 86400, "token_type": "Bearer"}, now=1000
    )
    assert token.expires_at == 1000 + 86400
    assert token.authorization_header() == "Bearer abc"


def test_is_expired_respects_leeway():
    token = AccessToken("abc", expires_at=1000 + 86400, token_type="Bearer")
    assert token.is_expired(leeway=60, now=1000) is False
    assert token.is_expired(leeway=60, now=1000 + 86400 - 30) is True
    assert token.is_expired(leeway=0, now=1000 + 86400) is True


def test_dict_round_trip():
    token = AccessToken("abc", expires_at=99999, token_type="Bearer")
    restored = AccessToken.from_dict(token.to_dict())
    assert restored == token
