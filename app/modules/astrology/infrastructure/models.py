import uuid
from datetime import UTC, date, datetime

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
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
    olimora_id: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        unique=True,
        index=True,
        default=lambda: f"oli_{uuid.uuid4().hex[:16]}",
    )
    password_hash: Mapped[str] = mapped_column(String(512), nullable=False)
    last_birth_profile_change_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    last_seen_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    status_message: Mapped[str | None] = mapped_column(String(60), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )

    birth_profile: Mapped["BirthProfileModel | None"] = relationship(
        back_populates="user", uselist=False
    )
    daily_readings: Mapped[list["DailyReadingModel"]] = relationship(
        back_populates="user", cascade="all, delete-orphan", passive_deletes=True
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


class DailyReadingModel(Base):
    __tablename__ = "daily_readings"
    __table_args__ = (
        UniqueConstraint("user_id", "reading_date", name="uq_daily_reading_user_date"),
        Index("ix_daily_readings_user_id_date", "user_id", "reading_date"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    reading_date: Mapped[date] = mapped_column(Date, nullable=False)
    main_theme: Mapped[str] = mapped_column(Text, nullable=False)
    relationships: Mapped[str] = mapped_column(Text, nullable=False)
    work_money: Mapped[str] = mapped_column(Text, nullable=False)
    caution: Mapped[str] = mapped_column(Text, nullable=False)
    source: Mapped[str] = mapped_column(String(30), nullable=False)
    model: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )

    user: Mapped[UserModel] = relationship(back_populates="daily_readings")


class DailySignReadingModel(Base):
    __tablename__ = "daily_sign_readings"
    __table_args__ = (
        UniqueConstraint("reading_date", "sign", name="uq_daily_sign_reading_date_sign"),
        Index("ix_daily_sign_readings_date_sign", "reading_date", "sign"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    reading_date: Mapped[date] = mapped_column(Date, nullable=False)
    sign: Mapped[str] = mapped_column(String(20), nullable=False)
    main_theme: Mapped[str] = mapped_column(Text, nullable=False)
    relationships: Mapped[str] = mapped_column(Text, nullable=False)
    work_money: Mapped[str] = mapped_column(Text, nullable=False)
    caution: Mapped[str] = mapped_column(Text, nullable=False)
    source: Mapped[str] = mapped_column(String(30), nullable=False)
    model: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )


class NatalInterpretationModel(Base):
    __tablename__ = "natal_interpretations"
    __table_args__ = (
        UniqueConstraint("user_id", "input_hash", name="uq_natal_interpretation_user_input"),
        Index("ix_natal_interpretations_user_id", "user_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    input_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    interpretation: Mapped[str] = mapped_column(Text, nullable=False)
    source: Mapped[str] = mapped_column(String(30), nullable=False)
    model: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )


class FriendshipModel(Base):
    __tablename__ = "friendships"
    __table_args__ = (
        UniqueConstraint("user_low_id", "user_high_id", name="uq_friendship_user_pair"),
        CheckConstraint("user_low_id <> user_high_id", name="ck_friendship_distinct_users"),
        CheckConstraint("status IN ('pending', 'accepted')", name="ck_friendship_status"),
        Index("ix_friendships_low_status", "user_low_id", "status"),
        Index("ix_friendships_high_status", "user_high_id", "status"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_low_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    user_high_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    requested_by_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )
    accepted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    messages: Mapped[list["DirectMessageModel"]] = relationship(
        back_populates="friendship", cascade="all, delete-orphan", passive_deletes=True
    )


class DirectMessageModel(Base):
    __tablename__ = "direct_messages"
    __table_args__ = (
        Index("ix_direct_messages_friendship_created", "friendship_id", "created_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    friendship_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("friendships.id", ondelete="CASCADE"), nullable=False
    )
    sender_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    body: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    friendship: Mapped[FriendshipModel] = relationship(back_populates="messages")


class FirebaseInstallationModel(Base):
    __tablename__ = "firebase_installations"
    __table_args__ = (Index("ix_firebase_installations_user_id", "user_id"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    fid: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    platform: Mapped[str] = mapped_column(String(20), nullable=False, default="android")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False
    )
