"""Add direct-message read state."""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260810_06"
down_revision: str | None = "20260809_05"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "direct_messages",
        sa.Column("read_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index(
        "ix_direct_messages_unread",
        "direct_messages",
        ["friendship_id", "sender_id", "read_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_direct_messages_unread", table_name="direct_messages")
    op.drop_column("direct_messages", "read_at")
