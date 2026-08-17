"""Add authenticated product feedback.

Revision ID: 20260817_13
Revises: 20260814_12
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "20260817_13"
down_revision: str | None = "20260814_12"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "product_feedback",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("category", sa.String(length=30), nullable=False),
        sa.Column("rating", sa.Integer(), nullable=False),
        sa.Column("details", sa.String(length=1000), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "category IN ('idea', 'bug', 'experience')",
            name="ck_product_feedback_category",
        ),
        sa.CheckConstraint("rating BETWEEN 1 AND 5", name="ck_product_feedback_rating"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_product_feedback_user_created",
        "product_feedback",
        ["user_id", "created_at"],
    )


def downgrade() -> None:
    op.drop_table("product_feedback")
