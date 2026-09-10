"""drop role column from users

Revision ID: c8103d7a5b42
Revises: fbdb3885535f
Create Date: 2026-09-09

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c8103d7a5b42'
down_revision: Union[str, Sequence[str], None] = 'fbdb3885535f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Drop the role column (roles now come from the Keycloak token)."""
    op.drop_column('users', 'role')


def downgrade() -> None:
    """Re-add the role column."""
    op.add_column(
        'users',
        sa.Column(
            'role',
            sa.String(length=20),
            server_default='student',
            nullable=False,
        ),
    )