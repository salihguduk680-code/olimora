"""Add public Olimora IDs and birth-profile edit cooldown state."""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260809_05"
down_revision: str | None = "20260809_04"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("users", sa.Column("olimora_id", sa.String(length=20), nullable=True))
    op.add_column(
        "users",
        sa.Column("last_birth_profile_change_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.execute(
        "UPDATE users SET olimora_id = 'oli_' || substr(replace(id::text, '-', ''), 1, 16) "
        "WHERE olimora_id IS NULL"
    )
    op.alter_column("users", "olimora_id", nullable=False)
    op.create_index("ix_users_olimora_id", "users", ["olimora_id"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_users_olimora_id", table_name="users")
    op.drop_column("users", "last_birth_profile_change_at")
    op.drop_column("users", "olimora_id")
