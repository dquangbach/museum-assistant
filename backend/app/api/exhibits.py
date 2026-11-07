from typing import Annotated
from urllib.parse import urlsplit

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import ValidationError
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.catalog import Limit, Offset, get_or_404
from app.core.security import require_admin
from app.db.session import get_session
from app.models.catalog import Exhibit, ExhibitAsset, Topic
from app.schemas.catalog import ExhibitCreate, ExhibitOut, ExhibitPatch, Page, QrResult
from app.services.exhibits import exhibit_output, write_exhibit

router = APIRouter()
admin_router = APIRouter(prefix="/admin", tags=["Admin"], dependencies=[Depends(require_admin)])
DB = Annotated[Session, Depends(get_session)]


def exhibit_page(db, statement, limit, offset):
    total = db.scalar(select(func.count()).select_from(statement.order_by(None).subquery()))
    rows = db.scalars(statement.order_by(Exhibit.id).limit(limit).offset(offset)).all()
    return {"items": [exhibit_output(db, row) for row in rows], "total": total, "limit": limit, "offset": offset}


@router.get("/exhibits", response_model=Page[ExhibitOut], tags=["Exhibits"])
def list_exhibits(db: DB, topic_id: str | None = None, q: Annotated[str | None, Query(max_length=200)] = None,
                  limit: Limit = 20, offset: Offset = 0):
    statement = select(Exhibit).where(Exhibit.is_published.is_(True))
    if topic_id:
        statement = statement.where(Exhibit.topic_id == topic_id)
    if q:
        statement = statement.where(Exhibit.name.ilike(f"%{q}%"))
    return exhibit_page(db, statement, limit, offset)


@router.get("/exhibits/{exhibit_id}", response_model=ExhibitOut, tags=["Exhibits"])
def get_exhibit(exhibit_id: str, db: DB):
    exhibit = get_or_404(db, Exhibit, exhibit_id)
    if not exhibit.is_published:
        raise HTTPException(404, "Not found")
    return exhibit_output(db, exhibit)


@router.get("/qr/resolve", response_model=QrResult, tags=["QR"])
def resolve_qr(db: DB, value: Annotated[str, Query(min_length=1, max_length=2048)]):
    try:
        parsed = urlsplit(value.strip())
    except ValueError:
        raise HTTPException(400, "Invalid QR payload")
    parts = parsed.path.split("/")
    if (parsed.scheme not in {"museum", "museum-demo"} or parsed.netloc not in {"topic", "exhibit"}
            or parsed.query or parsed.fragment or len(parts) != 2 or parts[0] or not parts[1]
            or not all(c in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_-" for c in parts[1])):
        raise HTTPException(400, "Expected museum://topic/ID or museum://exhibit/ID")
    identifier = parts[1].upper()
    if parsed.netloc == "topic":
        get_or_404(db, Topic, identifier)
        detail_url = f"/api/v1/topics/{identifier}"
    else:
        exhibit = get_or_404(db, Exhibit, identifier)
        if not exhibit.is_published:
            raise HTTPException(404, "Not found")
        detail_url = f"/api/v1/exhibits/{identifier}"
    return {"kind": parsed.netloc, "id": identifier, "detail_url": detail_url}


@admin_router.get("/exhibits", response_model=Page[ExhibitOut])
def admin_list(db: DB, limit: Limit = 20, offset: Offset = 0):
    return exhibit_page(db, select(Exhibit), limit, offset)


@admin_router.post("/exhibits", response_model=ExhibitOut, status_code=201)
def create_exhibit(data: ExhibitCreate, db: DB):
    return exhibit_output(db, write_exhibit(db, data))


@admin_router.patch("/exhibits/{exhibit_id}", response_model=ExhibitOut)
def update_exhibit(exhibit_id: str, data: ExhibitPatch, db: DB):
    exhibit = get_or_404(db, Exhibit, exhibit_id)
    current = {column.name: getattr(exhibit, column.name) for column in Exhibit.__table__.columns if column.name != "updated_at"}
    current["asset_ids"] = list(db.scalars(select(ExhibitAsset.asset_id).where(ExhibitAsset.exhibit_id == exhibit_id)
                                          .order_by(ExhibitAsset.sort_order)))
    current.update(data.model_dump(exclude_unset=True))
    try:
        merged = ExhibitCreate.model_validate(current)
    except ValidationError as error:
        raise HTTPException(422, error.errors(include_context=False))
    return exhibit_output(db, write_exhibit(db, merged, exhibit))
