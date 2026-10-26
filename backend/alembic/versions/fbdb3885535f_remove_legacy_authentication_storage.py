"""remove legacy authentication storage

Revision ID: fbdb3885535f
Revises: 7f4ffd64a291
Create Date: 2026-09-09
"""

from typing import Sequence, Union

from alembic import op


revision: str = "fbdb3885535f"
down_revision: Union[str, Sequence[str], None] = "7f4ffd64a291"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column("users", "email_verification_expires_at")
    op.drop_column("users", "email_verification_token_hash")
    op.drop_column("users", "password_hash")

    op.drop_index("ix_refresh_tokens_user_id", table_name="refresh_tokens")
    op.drop_index("ix_refresh_tokens_token_hash", table_name="refresh_tokens")
    op.drop_table("refresh_tokens")


def downgrade() -> None:
    raise NotImplementedError(
        "Downgrade is not supported for this authentication cleanup migration."
    )