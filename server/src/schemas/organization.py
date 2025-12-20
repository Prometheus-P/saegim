from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from src.models.organization import PlanType


class OrganizationBase(BaseModel):
    name: str
    plan_type: PlanType = PlanType.BASIC
    logo_url: Optional[str] = None

    # white-label (public)
    brand_name: Optional[str] = None
    brand_logo_url: Optional[str] = None
    brand_domain: Optional[str] = None
    hide_saegim: bool = False


class OrganizationCreate(OrganizationBase):
    pass


class OrganizationResponse(OrganizationBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
