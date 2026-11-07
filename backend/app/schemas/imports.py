from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class SourceRow(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    id: str = Field(min_length=1, max_length=64)


class GroupRow(SourceRow):
    title: str = Field(min_length=1, max_length=500)
    sort_order: int = Field(ge=0)
    directory: str = Field(max_length=1024)


class TopicRow(SourceRow):
    group_id: str = Field(min_length=1, max_length=64)
    catalog_number: int = Field(gt=0)
    title: str = Field(min_length=1, max_length=500)
    summary: str
    materials_notes: str
    source_reference: str
    review_status: Literal["needs_review", "verified"]
    directory: str = Field(max_length=1024)


class AssetRow(SourceRow):
    original_filename: str = Field(min_length=1, max_length=255)
    path: str = Field(min_length=1, max_length=1024)
    media_type: Literal["image/jpeg", "image/png", "image/webp", "image/heic"]
    size_bytes: int = Field(gt=0)
    sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    asset_role: str = Field(min_length=1, max_length=32)
    review_status: Literal["needs_review", "verified"]
    classification_status: Literal["assigned", "shared", "unassigned"]


class TopicAssetRow(BaseModel):
    model_config = ConfigDict(extra="forbid")
    topic_id: str = Field(min_length=1, max_length=64)
    asset_id: str = Field(min_length=1, max_length=64)
    sort_order: int = Field(ge=0)
    assignment_source: str = Field(max_length=255)
    review_status: Literal["needs_review", "verified"]
