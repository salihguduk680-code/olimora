"""Cache natal interpretations per user and chart input.

Revision ID: 20260812_10
Revises: 20260811_09
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "20260812_10"
down_revision: str | None = "20260811_09"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "natal_interpretations",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("input_hash", sa.String(length=64), nullable=False),
        sa.Column("interpretation", sa.Text(), nullable=False),
        sa.Column("source", sa.String(length=30), nullable=False),
        sa.Column("model", sa.String(length=100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "user_id", "input_hash", name="uq_natal_interpretation_user_input"
        ),
    )
    op.create_index(
        "ix_natal_interpretations_user_id",
        "natal_interpretations",
        ["user_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_natal_interpretations_user_id", table_name="natal_interpretations")
    op.drop_table("natal_interpretations")
