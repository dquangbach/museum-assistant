from fastapi import HTTPException
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models.catalog import Asset, Exhibit, ExhibitAsset, Topic
from app.schemas.catalog import AssetOut, ExhibitCreate


def asset_output(asset: Asset) -> AssetOut:
    return AssetOut(**{key: getattr(asset, key) for key in AssetOut.model_fields if key != "file_url"},
                    file_url=f"/api/v1/assets/{asset.id}/file")


def exhibit_output(session: Session, exhibit: Exhibit) -> dict:
    photos = session.scalars(select(Asset).join(ExhibitAsset, ExhibitAsset.asset_id == Asset.id)
                             .where(ExhibitAsset.exhibit_id == exhibit.id)
                             .order_by(ExhibitAsset.sort_order)).all()
    return {**{column.name: getattr(exhibit, column.name) for column in Exhibit.__table__.columns},
            "qr_payload": f"museum://exhibit/{exhibit.id}", "assets": [asset_output(a) for a in photos]}


def write_exhibit(session: Session, data: ExhibitCreate, exhibit: Exhibit | None = None) -> Exhibit:
    if session.get(Topic, data.topic_id) is None:
        raise HTTPException(422, "Unknown topic_id")
    if data.asset_ids:
        found = set(session.scalars(select(Asset.id).where(Asset.id.in_(data.asset_ids))).all())
        if found != set(data.asset_ids):
            raise HTTPException(422, "Unknown asset_ids")
    if exhibit is None:
        if session.get(Exhibit, data.id):
            raise HTTPException(409, "Exhibit ID already exists")
        exhibit = Exhibit()
        session.add(exhibit)
    for key, value in data.model_dump(exclude={"asset_ids"}).items():
        setattr(exhibit, key, value)
    session.flush()
    session.execute(delete(ExhibitAsset).where(ExhibitAsset.exhibit_id == data.id))
    session.add_all([ExhibitAsset(exhibit_id=data.id, asset_id=asset_id, sort_order=order)
                     for order, asset_id in enumerate(data.asset_ids)])
    session.commit()
    session.refresh(exhibit)
    return exhibit
