"""Add shared daily readings per zodiac sign.

Revision ID: 20260810_08
Revises: 20260810_07
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "20260810_08"
down_revision: str | None = "20260810_07"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "daily_sign_readings",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("reading_date", sa.Date(), nullable=False),
        sa.Column("sign", sa.String(length=20), nullable=False),
        sa.Column("main_theme", sa.Text(), nullable=False),
        sa.Column("relationships", sa.Text(), nullable=False),
        sa.Column("work_money", sa.Text(), nullable=False),
        sa.Column("caution", sa.Text(), nullable=False),
        sa.Column("source", sa.String(length=30), nullable=False),
        sa.Column("model", sa.String(length=100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("reading_date", "sign", name="uq_daily_sign_reading_date_sign"),
    )
    op.create_index(
        "ix_daily_sign_readings_date_sign", "daily_sign_readings", ["reading_date", "sign"]
    )


def downgrade() -> None:
    op.drop_index("ix_daily_sign_readings_date_sign", table_name="daily_sign_readings")
    op.drop_table("daily_sign_readings")
