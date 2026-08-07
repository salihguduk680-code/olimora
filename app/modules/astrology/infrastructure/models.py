import uuid
from datetime import UTC, datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class UserModel(Base):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint("btrim(email) <> ''", name="ck_user_email_not_blank"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(320), nullable=False, unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(512), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )

    birth_profile: Mapped["BirthProfileModel | None"] = relationship(
        back_populates="user", uselist=False
    )


class BirthProfileModel(Base):
    __tablename__ = "birth_profiles"
    __table_args__ = (
        CheckConstraint("btrim(name) <> ''", name="ck_birth_profile_name_not_blank"),
        CheckConstraint("latitude BETWEEN -90 AND 90", name="ck_birth_profile_latitude"),
        CheckConstraint("longitude BETWEEN -180 AND 180", name="ck_birth_profile_longitude"),
        CheckConstraint("fold IS NULL OR fold IN (0, 1)", name="ck_birth_profile_fold"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=True, unique=True
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    local_birth_datetime_naive: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False
    )
    timezone_name: Mapped[str] = mapped_column(String(100), nullable=False)
    resolved_utc_datetime: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    fold: Mapped[int | None] = mapped_column(Integer, nullable=True)
    utc_offset_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    place_name: Mapped[str] = mapped_column(String(200), nullable=False)
    tzdata_version: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False
    )

    natal_charts: Mapped[list["NatalChartModel"]] = relationship(
        back_populates="birth_profile",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    user: Mapped[UserModel | None] = relationship(back_populates="birth_profile")


class NatalChartModel(Base):
    __tablename__ = "natal_charts"
    __table_args__ = (
        UniqueConstraint(
            "birth_profile_id",
            "input_hash",
            name="uq_natal_chart_profile_input_hash",
        ),
        Index("ix_natal_charts_birth_profile_id", "birth_profile_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    birth_profile_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("birth_profiles.id", ondelete="CASCADE"),
        nullable=False,
    )
    calculator: Mapped[str] = mapped_column(String(100), nullable=False)
    calculator_version: Mapped[str] = mapped_column(String(50), nullable=False)
    wrapper_version: Mapped[str] = mapped_column(String(50), nullable=False)
    house_system: Mapped[str] = mapped_column(String(10), nullable=False)
    house_placement_method: Mapped[str] = mapped_column(String(100), nullable=False)
    zodiac_type: Mapped[str] = mapped_column(String(30), nullable=False)
    calculation_flags: Mapped[int] = mapped_column(Integer, nullable=False)
    input_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    result_json: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False)
    calculated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )

    birth_profile: Mapped[BirthProfileModel] = relationship(back_populates="natal_charts")
