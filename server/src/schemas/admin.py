from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from src.models.organization import PlanType
from src.schemas.order import OrderOut
from src.schemas.notification import NotificationLog


class OrganizationCreate(BaseModel):
    name: str
    plan_type: PlanType = PlanType.BASIC
    logo_url: Optional[str] = None
    # white-label (optional at create)
    brand_name: Optional[str] = None
    brand_logo_url: Optional[str] = None
    brand_domain: Optional[str] = None
    hide_saegim: Optional[bool] = None

    external_org_id: Optional[str] = None  # optional manual mapping (admin-key only)


class OrganizationUpdate(BaseModel):
    # internal
    name: Optional[str] = None
    logo_url: Optional[str] = None

    # white-label
    brand_name: Optional[str] = None
    brand_logo_url: Optional[str] = None
    brand_domain: Optional[str] = None
    hide_saegim: Optional[bool] = None

    # messaging templates (org override; optional)
    msg_alimtalk_template_sender: Optional[str] = None
    msg_alimtalk_template_recipient: Optional[str] = None
    msg_sms_template_sender: Optional[str] = None
    msg_sms_template_recipient: Optional[str] = None
    msg_kakao_template_code: Optional[str] = None
    msg_fallback_sms_enabled: Optional[bool] = None


class OrganizationOut(BaseModel):
    id: int
    name: str
    plan_type: PlanType
    logo_url: Optional[str] = None

    brand_name: Optional[str] = None
    brand_logo_url: Optional[str] = None
    brand_domain: Optional[str] = None
    hide_saegim: bool = False

    # messaging templates
    msg_alimtalk_template_sender: Optional[str] = None
    msg_alimtalk_template_recipient: Optional[str] = None
    msg_sms_template_sender: Optional[str] = None
    msg_sms_template_recipient: Optional[str] = None
    msg_kakao_template_code: Optional[str] = None
    msg_fallback_sms_enabled: Optional[bool] = None

    external_org_id: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class OrganizationLite(BaseModel):
    id: int
    name: str
    plan_type: PlanType
    logo_url: Optional[str] = None

    brand_name: Optional[str] = None
    brand_logo_url: Optional[str] = None
    brand_domain: Optional[str] = None
    hide_saegim: bool = False

    # messaging templates
    msg_alimtalk_template_sender: Optional[str] = None
    msg_alimtalk_template_recipient: Optional[str] = None
    msg_sms_template_sender: Optional[str] = None
    msg_sms_template_recipient: Optional[str] = None
    msg_kakao_template_code: Optional[str] = None
    msg_fallback_sms_enabled: Optional[bool] = None

    external_org_id: Optional[str] = None

    class Config:
        from_attributes = True


class MeOut(BaseModel):
    sub: str
    org_external_id: Optional[str] = None
    org_role: Optional[str] = None
    organization: Optional[OrganizationLite] = None

    class Config:
        from_attributes = True


class OrderDetailOut(BaseModel):
    order: OrderOut
    organization: OrganizationLite

    token: Optional[str] = None
    token_valid: bool = False

    upload_url: Optional[str] = None
    public_proof_url: Optional[str] = None
    short_public_url: Optional[str] = None

    proof_url: Optional[str] = None
    proof_uploaded_at: Optional[datetime] = None

    notifications: list[NotificationLog] = []


class LabelsIn(BaseModel):
    """Bulk label data request."""

    order_ids: list[int]
    ensure_tokens: bool = True
    # WARNING: force replaces existing token (breaks previously shared links)
    force: bool = False


class LabelOut(BaseModel):
    order_id: int
    order_number: str
    context: Optional[str] = None
    status: str

    token: str
    token_valid: bool

    upload_url: str
    public_proof_url: str

    organization_name: str
    organization_logo: Optional[str] = None
    hide_saegim: bool = False


class CsvImportError(BaseModel):
    row: int
    message: str


class CsvImportOut(BaseModel):
    created_count: int
    created_order_ids: list[int]
    errors: list[CsvImportError] = []
