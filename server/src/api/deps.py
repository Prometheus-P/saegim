"""
API dependencies.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Generator, Optional

from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session

from src.api.auth import require_admin
from src.core.database import SessionLocal
from src.models.organization import Organization, PlanType


@dataclass
class AuthContext:
    """Resolved auth context for multi-tenant scoping."""

    sub: str
    organization_id: Optional[int]  # internal DB org id (tenant)
    org_external_id: Optional[str]  # e.g. Clerk org_id
    org_role: Optional[str]
    is_admin_key: bool


def get_db() -> Generator[Session, None, None]:
    """
    Dependency for getting DB session.
    This is a copy of the one in core/database.py for convenience.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_auth_context(
    db: Session = Depends(get_db),
    claims: Dict[str, Any] = Depends(require_admin),
    x_org_id: Optional[int] = Header(default=None, alias="x-org-id"),
) -> AuthContext:
    """
    Resolve (user, org) context.
    - Bearer token (Clerk/Auth0/etc): uses org_id claim as tenant key; auto-provisions Organization row.
    - Admin key fallback: optionally pin org via X-Org-Id; otherwise org is None (platform scope).
    """
    sub = str(claims.get("sub") or "")
    is_admin_key = sub == "admin-key"

    # Clerk-style org claims
    org_external_id = (
        claims.get("org_id")
        or claims.get("orgId")
        or claims.get("organization_id")
        or claims.get("organizationId")
    )
    if isinstance(org_external_id, (int, float)):
        org_external_id = str(org_external_id)
    org_external_id = str(org_external_id) if org_external_id else None

    org_role = (
        claims.get("org_role")
        or claims.get("orgRole")
        or claims.get("organization_role")
        or claims.get("organizationRole")
    )
    org_role = str(org_role) if org_role else None

    if org_external_id:
        # map external org id -> internal organization row (tenant)
        org = db.query(Organization).filter(Organization.external_org_id == org_external_id).first()
        if not org:
            name_hint = (
                claims.get("org_name")
                or claims.get("orgName")
                or claims.get("org_slug")
                or claims.get("orgSlug")
                or f"Org {org_external_id[:8]}"
            )
            org = Organization(
                name=str(name_hint),
                plan_type=PlanType.BASIC,
                logo_url=None,
                external_org_id=org_external_id,
            )
            db.add(org)
            db.commit()
            db.refresh(org)

        return AuthContext(
            sub=sub,
            organization_id=org.id,
            org_external_id=org_external_id,
            org_role=org_role,
            is_admin_key=is_admin_key,
        )

    # No external org id in token
    if is_admin_key:
        if x_org_id is not None:
            org = db.query(Organization).filter(Organization.id == x_org_id).first()
            if not org:
                raise HTTPException(status_code=404, detail="ORG_NOT_FOUND")
            return AuthContext(
                sub=sub,
                organization_id=org.id,
                org_external_id=org.external_org_id,
                org_role="admin",
                is_admin_key=True,
            )

        # platform scope (dangerous): only allowed for admin-key in dev
        return AuthContext(sub=sub, organization_id=None, org_external_id=None, org_role="admin", is_admin_key=True)

    raise HTTPException(status_code=403, detail="ORG_REQUIRED")
