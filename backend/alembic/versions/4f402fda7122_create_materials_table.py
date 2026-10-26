"""create materials table

Revision ID: 4f402fda7122
Revises: 128458792565
Create Date: 2026-09-19 06:32:38.420923

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4f402fda7122'
down_revision: Union[str, Sequence[str], None] = '128458792565'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create the materials table."""
    op.create_table(
        "materials",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("course_id", sa.UUID(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("s3_key", sa.String(), nullable=False),
        sa.Column("status", sa.String(length=20), server_default="pending", nullable=False),
        sa.Column("uploaded_by", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["course_id"], ["courses.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["uploaded_by"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("s3_key", name="uq_materials_s3_key"),
    )
    op.create_index(op.f("ix_materials_course_id"), "materials", ["course_id"], unique=False)
    op.create_index(op.f("ix_materials_uploaded_by"), "materials", ["uploaded_by"], unique=False)


def downgrade() -> None:
    """Drop the materials table."""
    op.drop_index(op.f("ix_materials_uploaded_by"), table_name="materials")
    op.drop_index(op.f("ix_materials_course_id"), table_name="materials")
    op.drop_table("materials")
