"""add vector_records table for pgvector persistence

Revision ID: f3a1b7c9d4e2
Revises: c8103d7a5b42
Create Date: 2026-09-18
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "f3a1b7c9d4e2"
down_revision: Union[str, Sequence[str], None] = "c8103d7a5b42"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

TABLE_NAME = "vector_records"


def upgrade() -> None:
    # Fresh databases must be reproducible from migrations alone, so the
    # extension is created here (idempotent; already-enabled DBs unaffected).
    # CREATE EXTENSION is transactional on PostgreSQL 16, so this is safe
    # inside Alembic's default transaction.
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table(
        TABLE_NAME,
        sa.Column("id", sa.Text(), primary_key=True, nullable=False),
        sa.Column("embedding", Vector(1024), nullable=False),
        sa.Column("content", sa.Text(), nullable=True),
        sa.Column(
            "metadata",
            postgresql.JSONB(),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    # Deliberately NO ANN index for P9-B: exact cosine scans are correct and
    # fast at the expected scale (see design notes). Revisit HNSW when real
    # row counts/latency measurements justify it — adding one later requires
    # no table or provider change.


def downgrade() -> None:
    # Drop only what this migration created. The vector extension is NOT
    # dropped: other objects may use it, and dropping it would be destructive.
    op.drop_table(TABLE_NAME)
