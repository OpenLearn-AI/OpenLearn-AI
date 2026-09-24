"""restrict material status to supported values

Revision ID: b110ae6051f4
Revises: c462e4812d07
Create Date: 2026-09-24 09:15:00.671337

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'b110ae6051f4'
down_revision: Union[str, Sequence[str], None] = 'c462e4812d07'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Only 'pending', 'processing', 'ready', 'failed' are supported in W7."""
    op.create_check_constraint(
        'ck_materials_status_supported',
        'materials',
        "status IN ('pending', 'processing', 'ready', 'failed')",
    )


def downgrade() -> None:
    op.drop_constraint(
        'ck_materials_status_supported',
        'materials',
        type_='check',
    )