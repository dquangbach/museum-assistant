from datetime import datetime, timezone

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, Integer, MetaData, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention={
        "ix": "ix_%(column_0_label)s", "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s", "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    })


class Group(Base):
    __tablename__ = "groups"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    title: Mapped[str] = mapped_column(String(500))
    sort_order: Mapped[int] = mapped_column(Integer)
    directory: Mapped[str] = mapped_column(String(1024))


class Topic(Base):
    __tablename__ = "topics"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    group_id: Mapped[str] = mapped_column(ForeignKey("groups.id"), index=True)
    catalog_number: Mapped[int] = mapped_column(Integer, unique=True)
    title: Mapped[str] = mapped_column(String(500))
    summary: Mapped[str] = mapped_column(Text)
    materials_notes: Mapped[str] = mapped_column(Text)
    source_reference: Mapped[str] = mapped_column(Text)
    review_status: Mapped[str] = mapped_column(String(32), default="needs_review")
    directory: Mapped[str] = mapped_column(String(1024))


class Asset(Base):
    __tablename__ = "assets"
    __table_args__ = (CheckConstraint("size_bytes > 0", name="positive_size"),)
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    original_filename: Mapped[str] = mapped_column(String(255))
    path: Mapped[str] = mapped_column(String(1024), unique=True)
    media_type: Mapped[str] = mapped_column(String(64))
    size_bytes: Mapped[int] = mapped_column(Integer)
    sha256: Mapped[str] = mapped_column(String(64))
    asset_role: Mapped[str] = mapped_column(String(32), default="unclassified")
    review_status: Mapped[str] = mapped_column(String(32), default="needs_review")
    classification_status: Mapped[str] = mapped_column(String(32))


class TopicAsset(Base):
    __tablename__ = "topic_assets"
    topic_id: Mapped[str] = mapped_column(ForeignKey("topics.id", ondelete="CASCADE"), primary_key=True)
    asset_id: Mapped[str] = mapped_column(ForeignKey("assets.id", ondelete="CASCADE"), primary_key=True)
    sort_order: Mapped[int] = mapped_column(Integer)
    assignment_source: Mapped[str] = mapped_column(String(255))
    review_status: Mapped[str] = mapped_column(String(32))


class Exhibit(Base):
    __tablename__ = "exhibits"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    topic_id: Mapped[str] = mapped_column(ForeignKey("topics.id"), index=True)
    name: Mapped[str] = mapped_column(String(500))
    description: Mapped[str] = mapped_column(Text)
    period: Mapped[str | None] = mapped_column(String(255))
    material: Mapped[str | None] = mapped_column(String(255))
    floor: Mapped[str | None] = mapped_column(String(128))
    room: Mapped[str | None] = mapped_column(String(255))
    cabinet: Mapped[str | None] = mapped_column(String(255))
    review_status: Mapped[str] = mapped_column(String(32), default="needs_review")
    is_published: Mapped[bool] = mapped_column(Boolean, default=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class ExhibitAsset(Base):
    __tablename__ = "exhibit_assets"
    exhibit_id: Mapped[str] = mapped_column(ForeignKey("exhibits.id", ondelete="CASCADE"), primary_key=True)
    asset_id: Mapped[str] = mapped_column(ForeignKey("assets.id"), primary_key=True)
    sort_order: Mapped[int] = mapped_column(Integer)
