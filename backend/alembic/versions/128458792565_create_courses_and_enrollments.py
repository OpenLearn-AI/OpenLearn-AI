"""create courses and enrollments

Revision ID: 128458792565
Revises: 75d18b9eb2fe
Create Date: 2026-09-19 05:59:00.441832

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '128458792565'
down_revision: Union[str, Sequence[str], None] = '75d18b9eb2fe'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create the courses and enrollments tables."""
    op.create_table('courses',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('owner_id', sa.UUID(), nullable=False),
    sa.Column('title', sa.String(length=255), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_courses_owner_id'), 'courses', ['owner_id'], unique=False)
    op.create_table('enrollments',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('course_id', sa.UUID(), nullable=False),
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.ForeignKeyConstraint(['course_id'], ['courses.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('course_id', 'user_id', name='uq_enrollments_course_user')
    )
    op.create_index(op.f('ix_enrollments_user_id'), 'enrollments', ['user_id'], unique=False)


def downgrade() -> None:
    """Drop the enrollments and courses tables."""
    op.drop_index(op.f('ix_enrollments_user_id'), table_name='enrollments')
    op.drop_table('enrollments')
    op.drop_index(op.f('ix_courses_owner_id'), table_name='courses')
    op.drop_table('courses')
