"""merge migration heads

Revision ID: c462e4812d07
Revises: 4f402fda7122, f3a1b7c9d4e2
Create Date: 2026-09-19 08:57:21.683171

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c462e4812d07'
down_revision: Union[str, Sequence[str], None] = ('4f402fda7122', 'f3a1b7c9d4e2')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
