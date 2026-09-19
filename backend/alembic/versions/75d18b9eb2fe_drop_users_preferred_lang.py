"""drop users preferred lang

Revision ID: 75d18b9eb2fe
Revises: 6bee296ddce1
Create Date: 2026-09-18 20:31:26.642473

The preferred language now lives in profiles.preferred_language; users no
longer holds language data (single source of truth).

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '75d18b9eb2fe'
down_revision: Union[str, Sequence[str], None] = '6bee296ddce1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Drop the legacy users.preferred_lang column."""
    op.drop_column('users', 'preferred_lang')


def downgrade() -> None:
    """Restore users.preferred_lang with its original schema (bf5c36537834)."""
    op.add_column(
        'users',
        sa.Column(
            'preferred_lang',
            sa.String(length=10),
            server_default='en',
            nullable=False,
        ),
    )
