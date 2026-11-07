from datetime import datetime
from typing import Generic, Literal, TypeVar

from pydantic import BaseModel, ConfigDict, Field, model_validator

T = TypeVar("T")


class Page(BaseModel, Generic[T]):
    items: list[T]
    total: int
    limit: int
    offset: int


class OrmSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class GroupOut(OrmSchema):
    id: str
    title: str
    sort_order: int


class TopicOut(OrmSchema):
    id: str
    group_id: str
    catalog_number: int
    title: str
    summary: str
    materials_notes: str
    source_reference: str
    review_status: str


class AssetOut(BaseModel):
    id: str
    original_filename: str
    media_type: str
    size_bytes: int
    sha256: str
    asset_role: str
    review_status: str
    classification_status: str
    file_url: str


class ExhibitCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    id: str = Field(pattern=r"^[A-Z][A-Z0-9_-]{1,63}$")
    topic_id: str = Field(min_length=1, max_length=64)
    name: str = Field(min_length=1, max_length=500)
    description: str = Field(min_length=1)
    period: str | None = Field(default=None, max_length=255)
    material: str | None = Field(default=None, max_length=255)
    floor: str | None = Field(default=None, max_length=128)
    room: str | None = Field(default=None, max_length=255)
    cabinet: str | None = Field(default=None, max_length=255)
    review_status: Literal["needs_review", "verified"] = "needs_review"
    is_published: bool = False
    asset_ids: list[str] = Field(default_factory=list, max_length=100)

    @model_validator(mode="after")
    def check_publication(self):
        if self.is_published and self.review_status != "verified":
            raise ValueError("Verify exhibit information before publishing")
        if len(self.asset_ids) != len(set(self.asset_ids)):
            raise ValueError("asset_ids must not contain duplicates")
        return self


class ExhibitPatch(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    topic_id: str | None = None
    name: str | None = None
    description: str | None = None
    period: str | None = None
    material: str | None = None
    floor: str | None = None
    room: str | None = None
    cabinet: str | None = None
    review_status: Literal["needs_review", "verified"] | None = None
    is_published: bool | None = None
    asset_ids: list[str] | None = None


class ExhibitOut(OrmSchema):
    id: str
    topic_id: str
    name: str
    description: str
    period: str | None
    material: str | None
    floor: str | None
    room: str | None
    cabinet: str | None
    review_status: str
    is_published: bool
    updated_at: datetime
    qr_payload: str
    assets: list[AssetOut]


class QrResult(BaseModel):
    kind: Literal["exhibit", "topic"]
    id: str
    detail_url: str
