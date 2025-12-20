from __future__ import annotations

import time
from typing import Any, Dict, Optional

import httpx
from fastapi import Depends, Header, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt
from jose.exceptions import JWTError

from src.core.config import settings

bearer_scheme = HTTPBearer(auto_error=False)


class JWKSCache:
    def __init__(self, ttl_seconds: int = 3600):
        self.ttl = ttl_seconds
        self._cached_at = 0.0
        self._jwks: Optional[Dict[str, Any]] = None

    async def get(self) -> Dict[str, Any]:
        now = time.time()
        if self._jwks and (now - self._cached_at) < self.ttl:
            return self._jwks

        if not settings.AUTH_JWKS_URL:
            raise HTTPException(status_code=500, detail="AUTH_JWKS_URL_NOT_SET")

        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(settings.AUTH_JWKS_URL)
            if resp.status_code != 200:
                raise HTTPException(status_code=500, detail="AUTH_JWKS_FETCH_FAILED")
            self._jwks = resp.json()
            self._cached_at = now
            return self._jwks


jwks_cache = JWKSCache()


async def verify_bearer_token(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
) -> Dict[str, Any]:
    if not settings.AUTH_ENABLED:
        raise HTTPException(status_code=401, detail="AUTH_DISABLED")

    if not credentials or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="MISSING_BEARER_TOKEN")

    token = credentials.credentials

    try:
        jwks = await jwks_cache.get()
        # jose can pick the right key by 'kid' automatically if key is provided as JWKS
        claims = jwt.decode(
            token,
            jwks,
            algorithms=["RS256"],
            audience=settings.AUTH_AUDIENCE or None,
            issuer=settings.AUTH_ISSUER or None,
            options={
                "verify_aud": bool(settings.AUTH_AUDIENCE),
                "verify_iss": bool(settings.AUTH_ISSUER),
            },
        )
        return claims
    except JWTError:
        raise HTTPException(status_code=401, detail="INVALID_TOKEN")


async def require_admin(
    x_admin_key: Optional[str] = Header(default=None, alias="x-admin-key"),
    claims: Optional[Dict[str, Any]] = Depends(lambda: None),
    # NOTE: FastAPI can't conditionally run Depends easily; we do manual below.
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
) -> Dict[str, Any]:
    # 1) Prefer external auth if enabled and token present
    if settings.AUTH_ENABLED and credentials and credentials.scheme.lower() == "bearer":
        return await verify_bearer_token(credentials)

    # 2) Fallback: admin key (dev / emergency)
    if settings.ALLOW_ADMIN_API_KEY and x_admin_key and x_admin_key == settings.ADMIN_API_KEY:
        return {"sub": "admin-key", "role": "admin"}

    raise HTTPException(status_code=401, detail="UNAUTHORIZED")
