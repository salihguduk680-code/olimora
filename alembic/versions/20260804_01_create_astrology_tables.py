"""Create birth profile and natal chart tables."""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "20260804_01"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "birth_profiles",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("local_birth_datetime_naive", sa.DateTime(timezone=False), nullable=False),
        sa.Column("timezone_name", sa.String(length=100), nullable=False),
        sa.Column("resolved_utc_datetime", sa.DateTime(timezone=True), nullable=False),
        sa.Column("fold", sa.Integer(), nullable=True),
        sa.Column("utc_offset_minutes", sa.Integer(), nullable=False),
        sa.Column("latitude", sa.Float(), nullable=False),
        sa.Column("longitude", sa.Float(), nullable=False),
        sa.Column("place_name", sa.String(length=200), nullable=False),
        sa.Column("tzdata_version", sa.String(length=50), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("fold IS NULL OR fold IN (0, 1)", name="ck_birth_profile_fold"),
        sa.CheckConstraint("latitude BETWEEN -90 AND 90", name="ck_birth_profile_latitude"),
        sa.CheckConstraint("longitude BETWEEN -180 AND 180", name="ck_birth_profile_longitude"),
        sa.CheckConstraint("btrim(name) <> ''", name="ck_birth_profile_name_not_blank"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "natal_charts",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("birth_profile_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("calculator", sa.String(length=100), nullable=False),
        sa.Column("calculator_version", sa.String(length=50), nullable=False),
        sa.Column("wrapper_version", sa.String(length=50), nullable=False),
        sa.Column("house_system", sa.String(length=10), nullable=False),
        sa.Column("house_placement_method", sa.String(length=100), nullable=False),
        sa.Column("zodiac_type", sa.String(length=30), nullable=False),
        sa.Column("calculation_flags", sa.Integer(), nullable=False),
        sa.Column("input_hash", sa.String(length=64), nullable=False),
        sa.Column("result_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("calculated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["birth_profile_id"], ["birth_profiles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "birth_profile_id", "input_hash", name="uq_natal_chart_profile_input_hash"
        ),
    )
    op.create_index(
        "ix_natal_charts_birth_profile_id", "natal_charts", ["birth_profile_id"], unique=False
    )


def downgrade() -> None:
    op.drop_index("ix_natal_charts_birth_profile_id", table_name="natal_charts")
    op.drop_table("natal_charts")
    op.drop_table("birth_profiles")
