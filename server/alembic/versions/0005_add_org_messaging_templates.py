"""org messaging templates

Revision ID: 0005
Revises: 0004
Create Date: 2025-12-19

Adds per-organization messaging template overrides:
- msg_alimtalk_template_sender/recipient
- msg_sms_template_sender/recipient
- msg_kakao_template_code
- msg_fallback_sms_enabled
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0005"
down_revision = "0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("organizations", sa.Column("msg_alimtalk_template_sender", sa.Text(), nullable=True))
    op.add_column("organizations", sa.Column("msg_alimtalk_template_recipient", sa.Text(), nullable=True))
    op.add_column("organizations", sa.Column("msg_sms_template_sender", sa.Text(), nullable=True))
    op.add_column("organizations", sa.Column("msg_sms_template_recipient", sa.Text(), nullable=True))
    op.add_column("organizations", sa.Column("msg_kakao_template_code", sa.String(length=100), nullable=True))
    op.add_column("organizations", sa.Column("msg_fallback_sms_enabled", sa.Boolean(), nullable=True))


def downgrade() -> None:
    op.drop_column("organizations", "msg_fallback_sms_enabled")
    op.drop_column("organizations", "msg_kakao_template_code")
    op.drop_column("organizations", "msg_sms_template_recipient")
    op.drop_column("organizations", "msg_sms_template_sender")
    op.drop_column("organizations", "msg_alimtalk_template_recipient")
    op.drop_column("organizations", "msg_alimtalk_template_sender")
