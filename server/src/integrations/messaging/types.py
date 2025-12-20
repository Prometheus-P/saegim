from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class SendResult:
    request_id: Optional[str]
    raw: Any
