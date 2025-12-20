from __future__ import annotations

import uuid
from typing import Optional

from .base import MessagingProvider
from .types import SendResult


class MockMessagingProvider(MessagingProvider):
    name = "mock"

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
        return SendResult(request_id=f"mock-{uuid.uuid4().hex[:12]}", raw={"ok": True, "mode": "mock", "phone": phone})

    async def send_sms(
        self,
        *,
        phone: str,
        content: str,
        from_no: Optional[str] = None,
    ) -> SendResult:
        return SendResult(request_id=f"mock-{uuid.uuid4().hex[:12]}", raw={"ok": True, "mode": "mock", "phone": phone})
