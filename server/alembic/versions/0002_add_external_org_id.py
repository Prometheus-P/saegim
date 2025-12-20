"""add external_org_id to organizations

Revision ID: 0002
Revises: 0001
Create Date: 2025-12-19

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("organizations", sa.Column("external_org_id", sa.String(length=255), nullable=True))
    op.create_index(op.f("ix_organizations_external_org_id"), "organizations", ["external_org_id"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_organizations_external_org_id"), table_name="organizations")
    op.drop_column("organizations", "external_org_id")
