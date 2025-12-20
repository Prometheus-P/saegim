"""add org branding fields

Revision ID: 0003
Revises: 0002
Create Date: 2025-12-19

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("organizations", sa.Column("brand_name", sa.String(length=255), nullable=True))
    op.add_column("organizations", sa.Column("brand_logo_url", sa.String(length=500), nullable=True))
    op.add_column("organizations", sa.Column("brand_domain", sa.String(length=255), nullable=True))
    op.add_column(
        "organizations",
        sa.Column("hide_saegim", sa.Boolean(), nullable=False, server_default=sa.text("false")),
    )


def downgrade() -> None:
    op.drop_column("organizations", "hide_saegim")
    op.drop_column("organizations", "brand_domain")
    op.drop_column("organizations", "brand_logo_url")
    op.drop_column("organizations", "brand_name")
