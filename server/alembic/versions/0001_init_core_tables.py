"""init core tables

Revision ID: 0001
Revises:
Create Date: 2025-12-19

NOTE
- MVP 단계이므로, 초기 스키마는 이 마이그레이션을 기준으로 맞춘다.
- 모델(src/models)과 불일치하면 반드시 여기부터 고친다.
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create Enums first using raw SQL (most reliable approach)
    op.execute("CREATE TYPE plan_type AS ENUM ('BASIC', 'PRO')")
    op.execute("CREATE TYPE order_status AS ENUM ('PENDING', 'TOKEN_ISSUED', 'PROOF_UPLOADED', 'NOTIFIED', 'COMPLETED')")
    op.execute("CREATE TYPE notification_type AS ENUM ('SENDER', 'RECIPIENT')")
    op.execute("CREATE TYPE notification_channel AS ENUM ('ALIMTALK', 'SMS')")
    op.execute("CREATE TYPE notification_status AS ENUM ('PENDING', 'SENT', 'FAILED', 'FALLBACK_SENT', 'MOCK_SENT')")

    # Use PostgreSQL ENUM with create_type=False since we already created them
    plan_type = postgresql.ENUM("BASIC", "PRO", name="plan_type", create_type=False)
    order_status = postgresql.ENUM("PENDING", "TOKEN_ISSUED", "PROOF_UPLOADED", "NOTIFIED", "COMPLETED", name="order_status", create_type=False)
    notification_type = postgresql.ENUM("SENDER", "RECIPIENT", name="notification_type", create_type=False)
    notification_channel = postgresql.ENUM("ALIMTALK", "SMS", name="notification_channel", create_type=False)
    notification_status = postgresql.ENUM("PENDING", "SENT", "FAILED", "FALLBACK_SENT", "MOCK_SENT", name="notification_status", create_type=False)

    # organizations
    op.create_table(
        "organizations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("plan_type", plan_type, nullable=False, server_default="BASIC"),
        sa.Column("logo_url", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )

    # orders
    op.create_table(
        "orders",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("organization_id", sa.Integer(), nullable=False),
        sa.Column("order_number", sa.String(length=100), nullable=False),
        sa.Column("context", sa.String(length=500), nullable=True),
        sa.Column("sender_name", sa.String(length=100), nullable=False),
        sa.Column("sender_phone_encrypted", sa.Text(), nullable=False),
        sa.Column("recipient_name", sa.String(length=100), nullable=True),
        sa.Column("recipient_phone_encrypted", sa.Text(), nullable=True),
        sa.Column("status", order_status, nullable=False, server_default="PENDING"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("organization_id", "order_number", name="uq_orders_org_order_number"),
    )
    op.create_index("ix_orders_org_id", "orders", ["organization_id"])
    op.create_index("ix_orders_status", "orders", ["status"])

    # qr_tokens
    op.create_table(
        "qr_tokens",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("token", sa.String(length=32), nullable=False, unique=True),
        sa.Column("order_id", sa.Integer(), nullable=False, unique=True),
        sa.Column("is_valid", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["order_id"], ["orders.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_qr_tokens_token", "qr_tokens", ["token"])

    # proofs
    op.create_table(
        "proofs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("order_id", sa.Integer(), nullable=False, unique=True),
        sa.Column("file_path", sa.String(length=500), nullable=False),
        sa.Column("file_size", sa.Integer(), nullable=True),
        sa.Column("mime_type", sa.String(length=50), nullable=True),
        sa.Column("uploaded_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["order_id"], ["orders.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_proofs_order_id", "proofs", ["order_id"])

    # notifications
    op.create_table(
        "notifications",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("order_id", sa.Integer(), nullable=False),
        sa.Column("type", notification_type, nullable=False),
        sa.Column("channel", notification_channel, nullable=False),
        sa.Column("status", notification_status, nullable=False, server_default="PENDING"),
        sa.Column("phone_hash", sa.String(length=64), nullable=False),
        sa.Column("provider_request_id", sa.String(length=100), nullable=True),
        sa.Column("provider_response", sa.Text(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["order_id"], ["orders.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_notifications_order_id", "notifications", ["order_id"])
    op.create_index("ix_notifications_phone_hash", "notifications", ["phone_hash"])


def downgrade() -> None:
    op.drop_index("ix_notifications_phone_hash", table_name="notifications")
    op.drop_index("ix_notifications_order_id", table_name="notifications")
    op.drop_table("notifications")

    op.drop_index("ix_proofs_order_id", table_name="proofs")
    op.drop_table("proofs")

    op.drop_index("ix_qr_tokens_token", table_name="qr_tokens")
    op.drop_table("qr_tokens")

    op.drop_index("ix_orders_status", table_name="orders")
    op.drop_index("ix_orders_org_id", table_name="orders")
    op.drop_table("orders")

    op.drop_table("organizations")

    op.execute("DROP TYPE IF EXISTS notification_status")
    op.execute("DROP TYPE IF EXISTS notification_channel")
    op.execute("DROP TYPE IF EXISTS notification_type")
    op.execute("DROP TYPE IF EXISTS order_status")
    op.execute("DROP TYPE IF EXISTS plan_type")
