"""Add privacy-conscious user presence timestamps.

Revision ID: 20260811_09
Revises: 20260810_08
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260811_09"
down_revision: str | None = "20260810_08"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("users", sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("users", sa.Column("status_message", sa.String(length=60), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "status_message")
    op.drop_column("users", "last_seen_at")
