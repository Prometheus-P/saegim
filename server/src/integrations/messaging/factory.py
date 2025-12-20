from __future__ import annotations

from src.core.config import settings

from .base import MessagingProvider
from .kakao_i_connect import KakaoIConnectProvider
from .mock import MockMessagingProvider
from .naver_sens_sms import NaverSensSmsProvider


def get_primary_provider() -> MessagingProvider:
    p = (settings.MESSAGING_PROVIDER or "mock").strip().lower()

    if p == "mock":
        return MockMessagingProvider()

    if p in {"kakao", "kakao_i_connect", "kakaoiconnect"}:
        return KakaoIConnectProvider(settings.KAKAOI_BASE_URL, settings.KAKAOI_ACCESS_TOKEN)

    if p in {"sens_sms", "sens"}:
        return NaverSensSmsProvider(
            base_url=settings.SENS_BASE_URL,
            access_key=settings.SENS_ACCESS_KEY,
            secret_key=settings.SENS_SECRET_KEY,
            service_id=settings.SENS_SMS_SERVICE_ID,
            from_no=settings.SENS_SMS_FROM,
            country_code=settings.SENS_SMS_COUNTRY_CODE,
            content_type=settings.SENS_SMS_CONTENT_TYPE,
        )

    # unknown -> safe default
    return MockMessagingProvider()


def get_sms_provider() -> MessagingProvider:
    """Dedicated SMS provider for fallback (SENS)."""
    return NaverSensSmsProvider(
        base_url=settings.SENS_BASE_URL,
        access_key=settings.SENS_ACCESS_KEY,
        secret_key=settings.SENS_SECRET_KEY,
        service_id=settings.SENS_SMS_SERVICE_ID,
        from_no=settings.SENS_SMS_FROM,
        country_code=settings.SENS_SMS_COUNTRY_CODE,
        content_type=settings.SENS_SMS_CONTENT_TYPE,
    )
