"""widen learning_style_vark to 100 chars

Revision ID: a8f3d1c6e2b5
Revises: c5e8f1a2b9d7
Create Date: 2026-10-24 12:00:00.000000

The profile contract's `learning_style_vark` field is free text (the
product documents the four VARK styles its hint lists, joined by
commas). The previous 20-character column could not hold the full
comma-joined set ("Visual,Aural,Read/Write,Kinesthetic"), which broke
the onboarding wizard's genuine multi-select control. Widening to 100
keeps the free-form contract while matching the Batch 4.2 API and
frontend validation.
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = "a8f3d1c6e2b5"
down_revision: Union[str, Sequence[str], None] = "c5e8f1a2b9d7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "profiles",
        "learning_style_vark",
        existing_type=sa.String(length=20),
        type_=sa.String(length=100),
    )


def downgrade() -> None:
    op.alter_column(
        "profiles",
        "learning_style_vark",
        existing_type=sa.String(length=100),
        type_=sa.String(length=20),
    )
