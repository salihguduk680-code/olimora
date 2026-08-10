"""Add Firebase installation identifiers for push notifications.

Revision ID: 20260810_07
Revises: 20260810_06
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "20260810_07"
down_revision: str | None = "20260810_06"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "firebase_installations",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("fid", sa.String(length=255), nullable=False),
        sa.Column("platform", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("fid"),
    )
    op.create_index(
        "ix_firebase_installations_user_id", "firebase_installations", ["user_id"]
    )


def downgrade() -> None:
    op.drop_index("ix_firebase_installations_user_id", table_name="firebase_installations")
    op.drop_table("firebase_installations")
