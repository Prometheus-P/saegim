from __future__ import annotations


class MessagingError(Exception):
    """Base error with stable code for UI/DB."""

    def __init__(self, code: str, message: str, *, details: str | None = None):
        super().__init__(message)
        self.code = code
        self.details = details


class ConfigMissingError(MessagingError):
    def __init__(self, message: str, *, details: str | None = None):
        super().__init__("CONFIG_MISSING", message, details=details)


class ProviderHTTPError(MessagingError):
    def __init__(self, status_code: int, message: str, *, details: str | None = None):
        super().__init__(f"HTTP_{status_code}", message, details=details)
        self.status_code = status_code


class ProviderRejectedError(MessagingError):
    def __init__(self, code: str, message: str, *, details: str | None = None):
        super().__init__(code, message, details=details)
