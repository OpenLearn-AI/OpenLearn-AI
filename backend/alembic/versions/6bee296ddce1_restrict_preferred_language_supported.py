"""restrict preferred language to supported values

Revision ID: 6bee296ddce1
Revises: 0c4a02b4b578
Create Date: 2026-09-18 19:42:24.409606

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '6bee296ddce1'
down_revision: Union[str, Sequence[str], None] = '0c4a02b4b578'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Only 'en' and 'ar' are supported in v1.0 (ISO 639-1, lowercase)."""
    op.create_check_constraint(
        'ck_profiles_preferred_language_supported',
        'profiles',
        "preferred_language IN ('en', 'ar')",
    )


def downgrade() -> None:
    op.drop_constraint(
        'ck_profiles_preferred_language_supported',
        'profiles',
        type_='check',
    )
