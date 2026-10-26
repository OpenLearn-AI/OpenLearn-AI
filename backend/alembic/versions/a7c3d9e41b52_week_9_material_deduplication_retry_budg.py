"""week 9: material deduplication, retry budget, and material_pages

Revision ID: a7c3d9e41b52
Revises: b110ae6051f4
Create Date: 2026-10-20 12:00:00.000000

Adds materials.sha256 + uq_materials_course_sha256, materials.retry_count,
and the material_pages table.
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision: str = "a7c3d9e41b52"
down_revision: Union[str, Sequence[str], None] = "b110ae6051f4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add dedup/retry columns, the course+hash constraint, and material_pages."""
    op.add_column(
        "materials",
        sa.Column("sha256", sa.String(length=64), nullable=True),
    )
    op.add_column(
        "materials",
        sa.Column(
            "retry_count",
            sa.Integer(),
            server_default="0",
            nullable=False,
        ),
    )
    op.create_unique_constraint(
        "uq_materials_course_sha256",
        "materials",
        ["course_id", "sha256"],
    )
    op.create_table(
        "material_pages",
        sa.Column("id", UUID(as_uuid=True), nullable=False),
        sa.Column("material_id", UUID(as_uuid=True), nullable=False),
        sa.Column("page_number", sa.Integer(), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["material_id"],
            ["materials.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "material_id",
            "page_number",
            name="uq_material_pages_material_page",
        ),
        sa.CheckConstraint(
            "page_number >= 1",
            name="ck_material_pages_page_number_positive",
        ),
    )



def downgrade() -> None:
    """Reverse the Week 9 schema changes."""
    op.drop_table("material_pages")
    op.drop_constraint("uq_materials_course_sha256", "materials", type_="unique")
    op.drop_column("materials", "retry_count")
    op.drop_column("materials", "sha256")
