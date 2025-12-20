from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from .types import SendResult


class MessagingProvider(ABC):
    name: str

    @abstractmethod
    async def send_alimtalk(
        self,
        *,
        phone: str,
        message: str,
        sender_key: str,
        template_code: str,
        sender_no: Optional[str] = None,
        cid: Optional[str] = None,
        fall_back_yn: bool = False,
    ) -> SendResult:
        raise NotImplementedError

    @abstractmethod
    async def send_sms(
        self,
        *,
        phone: str,
        content: str,
        from_no: Optional[str] = None,
    ) -> SendResult:
        raise NotImplementedError
