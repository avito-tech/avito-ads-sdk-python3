"""Модель договора."""

from __future__ import annotations

from typing import Optional

from .advertiser import Advertiser
from .base import Model


class Contract(Model):
    """Договор."""

    @property
    def id(self) -> Optional[int]:
        return self._int("id")

    @property
    def account_id(self) -> Optional[int]:
        return self._int("accountID")

    @property
    def client(self) -> Advertiser:
        return Advertiser.from_dict(self._dict("client"))

    @property
    def contractor(self) -> Advertiser:
        return Advertiser.from_dict(self._dict("contractor"))

    @property
    def type(self) -> Optional[str]:
        return self._str("type")

    @property
    def date(self) -> Optional[str]:
        return self._str("date")

    @property
    def number(self) -> Optional[str]:
        return self._str("number")

    @property
    def subject(self) -> Optional[str]:
        return self._str("subject")

    @property
    def object(self) -> Optional[str]:
        return self._str("object")

    @property
    def cid(self) -> Optional[str]:
        return self._str("cid")

    @property
    def description(self) -> Optional[str]:
        return self._str("description")

    @property
    def parent_id(self) -> Optional[int]:
        return self._int("parentId")

    @property
    def is_agent_acting_for_publisher(self) -> Optional[bool]:
        """``isAgentActingForPublisher``; ``None``, если не задано."""
        return self._bool("isAgentActingForPublisher")

    @property
    def is_creative_reporter(self) -> Optional[bool]:
        """``isCreativeReporter``; ``None``, если не задано."""
        return self._bool("isCreativeReporter")
