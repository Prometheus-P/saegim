from __future__ import annotations

from typing import Optional

from datetime import date, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

from fastapi import HTTPException, BackgroundTasks
from sqlalchemy import or_
from sqlalchemy.orm import Session

from src.core.config import settings
from src.core.security import encrypt_phone, normalize_phone
from src.models import Organization, Order, OrderStatus, QRToken, Notification
from src.schemas.admin import OrganizationCreate
from src.schemas.order import OrderCreate
from src.schemas.notification import NotificationLog
from src.services.token_service import TokenService
from src.services.proof_service import ProofService
from src.services.notification_service import NotificationService
from src.services.short_link_service import ShortLinkService


class AdminService:
    """Backoffice service. Keep business logic out of routers."""

    def __init__(self, db: Session):
        self.db = db
        self.token_service = TokenService(db)
        self.proof_service = ProofService(db)
        self.notification_service = NotificationService(db)

    # ---------------------------
    # Organizations
    # ---------------------------
    def list_organizations(self, scope_org_id: Optional[int] = None) -> list[Organization]:
        q = self.db.query(Organization)
        if scope_org_id is not None:
            q = q.filter(Organization.id == scope_org_id)
        return q.order_by(Organization.id.asc()).all()

    def create_organization(self, payload: OrganizationCreate) -> Organization:
        org = Organization(
            name=payload.name,
            plan_type=payload.plan_type,
            logo_url=payload.logo_url,
            brand_name=getattr(payload, 'brand_name', None),
            brand_logo_url=getattr(payload, 'brand_logo_url', None),
            brand_domain=getattr(payload, 'brand_domain', None),
            hide_saegim=bool(getattr(payload, 'hide_saegim', False) or False),
            external_org_id=payload.external_org_id,
        )
        self.db.add(org)
        try:
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=400, detail=f"CREATE_ORG_FAILED: {e}") from e
        self.db.refresh(org)
        return org

    def update_organization(self, organization_id: int, payload) -> Organization:
        """Update organization settings (scoped org).

        v1: only name/logo + white-label fields.
        """
        org = self.db.query(Organization).filter(Organization.id == organization_id).first()
        if not org:
            raise HTTPException(status_code=404, detail="ORG_NOT_FOUND")

        def norm(v):
            if v is None:
                return None
            if isinstance(v, str):
                s = v.strip()
                return s if s else None
            return v

        fields_set = getattr(payload, '__fields_set__', None) or getattr(payload, 'model_fields_set', None) or set()

        # internal
        if getattr(payload, 'name', None) is not None:
            org.name = (payload.name or '').strip() or org.name
        if getattr(payload, 'logo_url', None) is not None:
            org.logo_url = norm(payload.logo_url)

        # white-label (public)
        if getattr(payload, 'brand_name', None) is not None:
            org.brand_name = norm(payload.brand_name)
        if getattr(payload, 'brand_logo_url', None) is not None:
            org.brand_logo_url = norm(payload.brand_logo_url)
        if getattr(payload, 'brand_domain', None) is not None:
            org.brand_domain = norm(payload.brand_domain)
        if getattr(payload, 'hide_saegim', None) is not None:
            org.hide_saegim = bool(payload.hide_saegim)

        # messaging templates (org override)
        if getattr(payload, 'msg_alimtalk_template_sender', None) is not None:
            org.msg_alimtalk_template_sender = norm(payload.msg_alimtalk_template_sender)
        if getattr(payload, 'msg_alimtalk_template_recipient', None) is not None:
            org.msg_alimtalk_template_recipient = norm(payload.msg_alimtalk_template_recipient)
        if getattr(payload, 'msg_sms_template_sender', None) is not None:
            org.msg_sms_template_sender = norm(payload.msg_sms_template_sender)
        if getattr(payload, 'msg_sms_template_recipient', None) is not None:
            org.msg_sms_template_recipient = norm(payload.msg_sms_template_recipient)

        if getattr(payload, 'msg_kakao_template_code', None) is not None:
            org.msg_kakao_template_code = norm(payload.msg_kakao_template_code)

        if 'msg_fallback_sms_enabled' in fields_set:
            # None => inherit global, otherwise override
            org.msg_fallback_sms_enabled = payload.msg_fallback_sms_enabled

        try:
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=400, detail=f"UPDATE_ORG_FAILED: {e}") from e

        self.db.refresh(org)
        return org

    # ---------------------------
    # Orders
    # ---------------------------
    def list_orders(
        self,
        organization_id: Optional[int] = None,
        q: Optional[str] = None,
        status: Optional[str] = None,
        day: Optional[str] = None,
        today: bool = False,
    ) -> list[Order]:
        query = self.db.query(Order)

        if organization_id is not None:
            query = query.filter(Order.organization_id == organization_id)

        if q:
            like = f"%{q.strip()}%"
            query = query.filter(
                or_(
                    Order.order_number.ilike(like),
                    Order.sender_name.ilike(like),
                    Order.recipient_name.ilike(like),
                    Order.context.ilike(like),
                )
            )

        if status:
            try:
                st = OrderStatus(status)
            except Exception:
                # allow lower/upper input
                try:
                    st = OrderStatus(status.upper())
                except Exception as e:
                    raise HTTPException(status_code=400, detail=f"INVALID_STATUS: {status}") from e
            query = query.filter(Order.status == st)

        # Date filter (Asia/Seoul by default)
        if today or day:
            try:
                if today:
                    kst = ZoneInfo("Asia/Seoul")
                    d: date = datetime.now(timezone.utc).astimezone(kst).date()
                else:
                    d = date.fromisoformat((day or "").strip())
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"INVALID_DAY: {day}") from e

            kst = ZoneInfo("Asia/Seoul")
            start_kst = datetime.combine(d, time.min).replace(tzinfo=kst)
            end_kst = start_kst + timedelta(days=1)
            start_utc = start_kst.astimezone(timezone.utc)
            end_utc = end_kst.astimezone(timezone.utc)
            query = query.filter(Order.created_at >= start_utc).filter(Order.created_at < end_utc)

        return query.order_by(Order.created_at.desc()).all()

    def import_orders_csv(
        self,
        rows: list[dict],
        organization_id: int,
        *,
        strict: bool = False,
    ) -> tuple[list[int], list[dict]]:
        """Import many orders from parsed CSV rows.

        Args:
            rows: list of dict rows. Expected keys:
              - order_number
              - context (optional)
              - sender_name
              - sender_phone
              - recipient_name (optional)
              - recipient_phone (optional)
            strict: if True, any row error aborts whole import.

        Returns:
            (created_order_ids, errors)
        """

        org = self.db.query(Organization).filter(Organization.id == organization_id).first()
        if not org:
            raise HTTPException(status_code=404, detail="ORG_NOT_FOUND")

        created_ids: list[int] = []
        errors: list[dict] = []

        for idx, r in enumerate(rows, start=1):
            try:
                order_number = (r.get("order_number") or r.get("order_no") or "").strip()
                if not order_number:
                    raise ValueError("ORDER_NUMBER_REQUIRED")

                sender_name = (r.get("sender_name") or r.get("buyer_name") or "").strip()
                if not sender_name:
                    raise ValueError("SENDER_NAME_REQUIRED")

                sender_phone_raw = (r.get("sender_phone") or r.get("buyer_phone") or "").strip()
                if not sender_phone_raw:
                    raise ValueError("SENDER_PHONE_REQUIRED")

                sender_phone = normalize_phone(sender_phone_raw)
                sender_enc = encrypt_phone(sender_phone)

                recipient_name = (r.get("recipient_name") or r.get("receiver_name") or "").strip() or None
                recipient_phone_raw = (r.get("recipient_phone") or r.get("receiver_phone") or "").strip() or None

                recipient_enc = None
                if recipient_phone_raw:
                    recipient_phone = normalize_phone(recipient_phone_raw)
                    recipient_enc = encrypt_phone(recipient_phone)

                context = (r.get("context") or r.get("event") or "").strip() or None

                order = Order(
                    organization_id=organization_id,
                    order_number=order_number,
                    context=context,
                    sender_name=sender_name,
                    sender_phone_encrypted=sender_enc,
                    recipient_name=recipient_name,
                    recipient_phone_encrypted=recipient_enc,
                    status=OrderStatus.PENDING,
                )
                self.db.add(order)
                self.db.flush()  # assign PK
                created_ids.append(order.id)
            except Exception as e:
                err = {"row": idx, "message": str(e)}
                errors.append(err)
                if strict:
                    self.db.rollback()
                    raise HTTPException(status_code=400, detail=f"CSV_IMPORT_FAILED: row {idx}: {e}") from e

        try:
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=400, detail=f"CSV_IMPORT_COMMIT_FAILED: {e}") from e

        return created_ids, errors

    def create_order(self, payload: OrderCreate, organization_id: int) -> Order:
        org = self.db.query(Organization).filter(Organization.id == organization_id).first()
        if not org:
            raise HTTPException(status_code=404, detail="ORG_NOT_FOUND")

        order_number = (payload.order_number or "").strip()
        if not order_number:
            raise HTTPException(status_code=400, detail="ORDER_NUMBER_REQUIRED")

        # normalize + encrypt phones
        sender_phone = normalize_phone(payload.sender_phone)
        sender_enc = encrypt_phone(sender_phone)

        recipient_enc = None
        if payload.recipient_phone:
            recipient_phone = normalize_phone(payload.recipient_phone)
            recipient_enc = encrypt_phone(recipient_phone)

        order = Order(
            organization_id=organization_id,
            order_number=order_number,
            context=(payload.context.strip() if payload.context else None),
            sender_name=payload.sender_name.strip(),
            sender_phone_encrypted=sender_enc,
            recipient_name=(payload.recipient_name.strip() if payload.recipient_name else None),
            recipient_phone_encrypted=recipient_enc,
            status=OrderStatus.PENDING,
        )
        self.db.add(order)
        self.db.commit()
        self.db.refresh(order)
        return order

    def get_order_detail(self, order_id: int, scope_org_id: Optional[int] = None) -> dict:
        q = self.db.query(Order).filter(Order.id == order_id)
        if scope_org_id is not None:
            q = q.filter(Order.organization_id == scope_org_id)
        order = q.first()
        if not order:
            raise HTTPException(status_code=404, detail="ORDER_NOT_FOUND")

        org = order.organization
        qr: Optional[QRToken] = order.qr_token
        proof = order.proof

        token = qr.token if qr else None
        token_valid = bool(qr and qr.is_valid)

        upload_url = f"{settings.WEB_BASE_URL}/proof/{token}" if token else None
        public_proof_url = f"{settings.WEB_BASE_URL}/p/{token}" if token else None

        short_public_url = None
        if token:
            sl = ShortLinkService(self.db).get_or_create_public_proof(order_id=order.id, token=token)
            short_public_url = f"{settings.WEB_BASE_URL}/s/{sl.code}"

        proof_url = None
        proof_uploaded_at = None
        if proof:
            proof_url = f"{settings.APP_BASE_URL}/uploads/{proof.file_path}"
            proof_uploaded_at = proof.uploaded_at

        notifications = (
            self.db.query(Notification)
            .filter(Notification.order_id == order.id)
            .order_by(Notification.created_at.desc())
            .all()
        )
        notifications_out = [NotificationLog.model_validate(n).model_dump() for n in notifications]

        return {
            "order": order,
            "organization": org,
            "token": token,
            "token_valid": token_valid,
            "upload_url": upload_url,
            "public_proof_url": public_proof_url,
            "short_public_url": short_public_url,
            "proof_url": proof_url,
            "proof_uploaded_at": proof_uploaded_at,
            "notifications": notifications_out,
        }

    def issue_token(self, order_id: int, scope_org_id: Optional[int] = None, force: bool = False) -> dict:
        q = self.db.query(Order).filter(Order.id == order_id)
        if scope_org_id is not None:
            q = q.filter(Order.organization_id == scope_org_id)
        order = q.first()
        if not order:
            raise HTTPException(status_code=404, detail="ORDER_NOT_FOUND")

        existing = order.qr_token
        if existing and existing.is_valid and not force:
            token = existing.token
            return {
                "token": token,
                "token_valid": True,
                "upload_url": f"{settings.WEB_BASE_URL}/proof/{token}",
                "public_proof_url": f"{settings.WEB_BASE_URL}/p/{token}",
            }

        # If existing token present, delete it to satisfy (order_id) unique constraint
        if existing:
            self.db.delete(existing)
            self.db.commit()

        qr_token = self.token_service.create_token_for_order(order.id)
        order.status = OrderStatus.TOKEN_ISSUED
        self.db.commit()

        token = qr_token.token
        return {
            "token": token,
            "token_valid": True,
            "upload_url": f"{settings.WEB_BASE_URL}/proof/{token}",
            "public_proof_url": f"{settings.WEB_BASE_URL}/p/{token}",
        }

    def get_labels(
        self,
        order_ids: list[int],
        scope_org_id: int,
        ensure_tokens: bool = True,
        force: bool = False,
    ) -> list[dict]:
        """Return print-friendly label data for many orders.

        Default behavior is "safe":
        - If token exists, keep it.
        - If token missing and ensure_tokens=True, issue a token.
        - If force=True, replace token (breaks previously shared links).
        """

        if not order_ids:
            return []

        # De-dup while keeping order
        seen = set()
        ids: list[int] = []
        for oid in order_ids:
            if oid in seen:
                continue
            seen.add(oid)
            ids.append(oid)

        orders = (
            self.db.query(Order)
            .filter(Order.organization_id == scope_org_id)
            .filter(Order.id.in_(ids))
            .all()
        )
        by_id = {o.id: o for o in orders}

        out: list[dict] = []
        changed = False

        for oid in ids:
            order = by_id.get(oid)
            if not order:
                # keep response stable for the rest; caller can show error per id
                raise HTTPException(status_code=404, detail=f"ORDER_NOT_FOUND:{oid}")

            org = order.organization
            existing = order.qr_token

            if (existing is None) and ensure_tokens:
                qr_token = self.token_service.create_token_for_order(order.id)
                order.status = OrderStatus.TOKEN_ISSUED
                existing = qr_token
                changed = True

            if existing and force:
                # WARNING: This replaces token (breaks old links).
                self.db.delete(existing)
                self.db.commit()
                qr_token = self.token_service.create_token_for_order(order.id)
                order.status = OrderStatus.TOKEN_ISSUED
                existing = qr_token
                changed = True

            if not existing:
                # still no token (ensure_tokens=False)
                continue

            token = existing.token
            token_valid = bool(existing.is_valid)
            upload_url = f"{settings.WEB_BASE_URL}/proof/{token}"
            public_proof_url = f"{settings.WEB_BASE_URL}/p/{token}"

            out.append(
                {
                    "order_id": order.id,
                    "order_number": order.order_number,
                    "context": order.context,
                    "status": str(order.status),
                    "token": token,
                    "token_valid": token_valid,
                    "upload_url": upload_url,
                    "public_proof_url": public_proof_url,
                    "organization_name": (org.brand_name or org.name),
                    "organization_logo": (org.brand_logo_url or org.logo_url),
                    "hide_saegim": bool(org.hide_saegim),
                }
            )

        if changed:
            self.db.commit()

        return out

    async def resend_notification(
        self,
        order_id: int,
        background_tasks: BackgroundTasks,
        scope_org_id: Optional[int] = None,
    ) -> dict:
        q = self.db.query(Order).filter(Order.id == order_id)
        if scope_org_id is not None:
            q = q.filter(Order.organization_id == scope_org_id)
        order = q.first()
        if not order:
            raise HTTPException(status_code=404, detail="ORDER_NOT_FOUND")

        if not order.proof:
            raise HTTPException(status_code=400, detail="PROOF_NOT_UPLOADED")

        await self.notification_service.send_dual_notification(order=order, background_tasks=background_tasks)
        return {"status": "ok"}
