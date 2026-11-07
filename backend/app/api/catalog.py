from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import FileResponse
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.session import get_session
from app.models.catalog import Asset, Group, Topic, TopicAsset
from app.schemas.catalog import AssetOut, GroupOut, Page, TopicOut
from app.services.exhibits import asset_output
from app.services.media import resolve_asset_path

router = APIRouter()
DB = Annotated[Session, Depends(get_session)]
Limit = Annotated[int, Query(ge=1, le=100)]
Offset = Annotated[int, Query(ge=0)]


def page(session, statement, limit, offset):
    total = session.scalar(select(func.count()).select_from(statement.order_by(None).subquery()))
    return {"items": session.scalars(statement.limit(limit).offset(offset)).all(),
            "total": total, "limit": limit, "offset": offset}


def get_or_404(session, model, identifier):
    result = session.get(model, identifier)
    if result is None:
        raise HTTPException(404, "Not found")
    return result


@router.get("/groups", response_model=list[GroupOut], tags=["Groups"])
def list_groups(db: DB):
    return db.scalars(select(Group).order_by(Group.sort_order, Group.id)).all()


@router.get("/groups/{group_id}", response_model=GroupOut, tags=["Groups"])
def get_group(group_id: str, db: DB):
    return get_or_404(db, Group, group_id)


@router.get("/topics", response_model=Page[TopicOut], tags=["Topics"])
def list_topics(db: DB, group_id: str | None = None, q: Annotated[str | None, Query(max_length=200)] = None,
                limit: Limit = 20, offset: Offset = 0):
    statement = select(Topic)
    if group_id:
        statement = statement.where(Topic.group_id == group_id)
    if q:
        statement = statement.where(Topic.title.ilike(f"%{q}%"))
    return page(db, statement.order_by(Topic.catalog_number, Topic.id), limit, offset)


@router.get("/topics/{topic_id}", response_model=TopicOut, tags=["Topics"])
def get_topic(topic_id: str, db: DB):
    return get_or_404(db, Topic, topic_id)


@router.get("/topics/{topic_id}/assets", response_model=Page[AssetOut], tags=["Topics"])
def topic_assets(topic_id: str, db: DB, limit: Limit = 20, offset: Offset = 0):
    get_or_404(db, Topic, topic_id)
    statement = select(Asset).join(TopicAsset, TopicAsset.asset_id == Asset.id).where(TopicAsset.topic_id == topic_id)
    result = page(db, statement.order_by(TopicAsset.sort_order, Asset.id), limit, offset)
    result["items"] = [asset_output(asset) for asset in result["items"]]
    return result


@router.get("/assets", response_model=Page[AssetOut], tags=["Assets"])
def list_assets(db: DB, classification_status: Annotated[str | None, Query(pattern="^(assigned|shared|unassigned)$")] = None,
                limit: Limit = 20, offset: Offset = 0):
    statement = select(Asset)
    if classification_status:
        statement = statement.where(Asset.classification_status == classification_status)
    result = page(db, statement.order_by(Asset.original_filename, Asset.id), limit, offset)
    result["items"] = [asset_output(asset) for asset in result["items"]]
    return result


@router.get("/assets/{asset_id}", response_model=AssetOut, tags=["Assets"])
def get_asset(asset_id: str, db: DB):
    return asset_output(get_or_404(db, Asset, asset_id))


@router.get("/assets/{asset_id}/file", response_class=FileResponse, tags=["Assets"])
def asset_file(asset_id: str, request: Request, db: DB):
    asset = get_or_404(db, Asset, asset_id)
    try:
        path = resolve_asset_path(request.app.state.settings.dataset_dir, asset.path)
    except (ValueError, FileNotFoundError):
        raise HTTPException(404, "Asset file is unavailable")
    return FileResponse(path, media_type=asset.media_type, headers={"X-Content-Type-Options": "nosniff"})
