"""Store one on-demand Athena reading per user and local day."""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "20260809_03"
down_revision: str | None = "20260807_02"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "daily_readings",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("reading_date", sa.Date(), nullable=False),
        sa.Column("main_theme", sa.Text(), nullable=False),
        sa.Column("relationships", sa.Text(), nullable=False),
        sa.Column("work_money", sa.Text(), nullable=False),
        sa.Column("caution", sa.Text(), nullable=False),
        sa.Column("source", sa.String(length=30), nullable=False),
        sa.Column("model", sa.String(length=100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "reading_date", name="uq_daily_reading_user_date"),
    )
    op.create_index("ix_daily_readings_user_id_date", "daily_readings", ["user_id", "reading_date"])


def downgrade() -> None:
    op.drop_index("ix_daily_readings_user_id_date", table_name="daily_readings")
    op.drop_table("daily_readings")
