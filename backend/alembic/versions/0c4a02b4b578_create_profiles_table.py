"""create profiles table

Revision ID: 0c4a02b4b578
Revises: c8103d7a5b42
Create Date: 2026-09-18 17:45:27.297180

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0c4a02b4b578'
down_revision: Union[str, Sequence[str], None] = 'c8103d7a5b42'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create the profiles table (Week 6 CSP subset, one profile per user)."""
    op.create_table('profiles',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('education_level', sa.String(length=50), nullable=True),
    sa.Column('major', sa.String(length=255), nullable=True),
    sa.Column('university', sa.String(length=255), nullable=True),
    sa.Column('preferred_language', sa.String(length=10), server_default='en', nullable=False),
    sa.Column('learning_style_vark', sa.String(length=20), nullable=True),
    sa.Column('daily_available_minutes', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.CheckConstraint(
        "daily_available_minutes IS NULL OR "
        "(daily_available_minutes >= 1 AND daily_available_minutes <= 1440)",
        name='ck_profiles_daily_available_minutes_range',
    ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('user_id', name='uq_profiles_user_id')
    )


def downgrade() -> None:
    """Drop the profiles table."""
    op.drop_table('profiles')
