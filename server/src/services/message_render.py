from __future__ import annotations

from typing import Dict


class _SafeDict(dict):
    def __missing__(self, key: str):
        return ""


def render(template: str, context: Dict[str, str]) -> str:
    """Small, safe template renderer.

    Placeholders use Python format syntax, e.g.:
    - {brand} {url} {order}
    - {context} {sender} {recipient}

    Missing keys become empty strings.
    """
    if template is None:
        return ""
    safe = _SafeDict({k: (v or "") for k, v in (context or {}).items()})
    try:
        return template.format_map(safe)
    except Exception:
        # Fail-closed: return raw template without formatting
        return template
