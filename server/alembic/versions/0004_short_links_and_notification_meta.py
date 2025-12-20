"""short links + notification meta

Revision ID: 0004
Revises: 0003
Create Date: 2025-12-19

Adds:
- short_links: short code -> target token/url
- notifications.message_url / notifications.error_code
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "short_links",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("code", sa.String(length=12), nullable=False, unique=True),
        sa.Column("order_id", sa.Integer(), nullable=False),
        sa.Column("target_token", sa.String(length=32), nullable=False),
        sa.Column("target_path", sa.String(length=255), nullable=False, server_default="/p"),
        sa.Column("click_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_clicked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["order_id"], ["orders.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("order_id", name="uq_short_links_order_id"),
    )
    op.create_index("ix_short_links_code", "short_links", ["code"], unique=True)

    # notifications meta
    op.add_column("notifications", sa.Column("message_url", sa.String(length=1024), nullable=True))
    op.add_column("notifications", sa.Column("error_code", sa.String(length=64), nullable=True))


def downgrade() -> None:
    op.drop_column("notifications", "error_code")
    op.drop_column("notifications", "message_url")

    op.drop_index("ix_short_links_code", table_name="short_links")
    op.drop_table("short_links")
