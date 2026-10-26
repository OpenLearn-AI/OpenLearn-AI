"""week 9 review hardening: s3_etag, updated_at, vector metadata index

Revision ID: c5e8f1a2b9d7
Revises: a7c3d9e41b52
Create Date: 2026-10-21 12:00:00.000000

Adds materials.s3_etag (object version pinned at registration),
materials.updated_at (stuck-material reaper), and a GIN index on
vector_records.metadata so the ``metadata @> {...}`` filter used to delete a
material's vectors no longer scans the whole table.
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = "c5e8f1a2b9d7"
down_revision: Union[str, Sequence[str], None] = "a7c3d9e41b52"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "materials",
        sa.Column("s3_etag", sa.String(length=128), nullable=True),
    )
    op.add_column(
        "materials",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
    )
    op.create_index(
        "ix_vector_records_metadata_gin",
        "vector_records",
        ["metadata"],
        postgresql_using="gin",
        postgresql_ops={"metadata": "jsonb_path_ops"},
    )


def downgrade() -> None:
    op.drop_index("ix_vector_records_metadata_gin", table_name="vector_records")
    op.drop_column("materials", "updated_at")
    op.drop_column("materials", "s3_etag")
