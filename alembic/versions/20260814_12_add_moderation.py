"""Add blocking, user reports, and Athena feedback.

Revision ID: 20260814_12
Revises: 20260813_11
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "20260814_12"
down_revision: str | None = "20260813_11"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("users", sa.Column("display_name", sa.String(length=30), nullable=True))
    op.add_column(
        "daily_readings",
        sa.Column("is_favorite", sa.Boolean(), server_default=sa.false(), nullable=False),
    )
    op.create_table(
        "user_blocks",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("blocker_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("blocked_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("blocker_id <> blocked_id", name="ck_user_block_distinct_users"),
        sa.ForeignKeyConstraint(["blocked_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["blocker_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("blocker_id", "blocked_id", name="uq_user_block_pair"),
    )
    op.create_index("ix_user_blocks_blocker_id", "user_blocks", ["blocker_id"])
    op.create_index("ix_user_blocks_blocked_id", "user_blocks", ["blocked_id"])
    op.create_table(
        "user_reports",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("reporter_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("reported_user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("message_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("reason", sa.String(length=30), nullable=False),
        sa.Column("details", sa.String(length=500), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("reporter_id <> reported_user_id", name="ck_user_report_distinct_users"),
        sa.CheckConstraint("reason IN ('spam', 'harassment', 'inappropriate', 'other')", name="ck_user_report_reason"),
        sa.ForeignKeyConstraint(["message_id"], ["direct_messages.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["reported_user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["reporter_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_user_reports_reporter_created", "user_reports", ["reporter_id", "created_at"])
    op.create_table(
        "content_feedback",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("content_type", sa.String(length=30), nullable=False),
        sa.Column("reason", sa.String(length=30), nullable=False),
        sa.Column("details", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("content_type IN ('natal', 'daily_sign', 'daily_premium')", name="ck_content_feedback_type"),
        sa.CheckConstraint("reason IN ('unsafe', 'incorrect', 'offensive', 'other')", name="ck_content_feedback_reason"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_content_feedback_user_created", "content_feedback", ["user_id", "created_at"])


def downgrade() -> None:
    op.drop_table("content_feedback")
    op.drop_table("user_reports")
    op.drop_table("user_blocks")
    op.drop_column("users", "display_name")
    op.drop_column("daily_readings", "is_favorite")
