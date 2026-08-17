"""Create users and connect one saved birth profile per user."""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "20260807_02"
down_revision: str | None = "20260804_01"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("password_hash", sa.String(length=512), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("btrim(email) <> ''", name="ck_user_email_not_blank"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_unique_constraint("uq_birth_profiles_user_id", "birth_profiles", ["user_id"])
    op.create_foreign_key(
        "fk_birth_profiles_user_id_users",
        "birth_profiles",
        "users",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    op.drop_constraint("fk_birth_profiles_user_id_users", "birth_profiles", type_="foreignkey")
    op.drop_constraint("uq_birth_profiles_user_id", "birth_profiles", type_="unique")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
