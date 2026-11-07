import hashlib
import json
from pathlib import Path

from pydantic import TypeAdapter
from sqlalchemy.orm import Session

from app.models.catalog import Asset, Group, Topic, TopicAsset
from app.schemas.imports import AssetRow, GroupRow, TopicAssetRow, TopicRow
from app.services.media import resolve_asset_path


def import_dataset(session: Session, dataset: Path) -> dict[str, int]:
    """Validate the complete batch before writing; caller owns the transaction."""
    def load(name, schema):
        rows = TypeAdapter(list[schema]).validate_python(json.loads((dataset / "metadata" / f"{name}.json").read_text(encoding="utf-8")))
        keys = [(row.topic_id, row.asset_id) if name == "topic_assets" else row.id for row in rows]
        if len(keys) != len(set(keys)):
            raise ValueError(f"Duplicate keys in {name}")
        return rows

    groups = load("groups", GroupRow)
    topics = load("topics", TopicRow)
    assets = load("assets", AssetRow)
    links = load("topic_assets", TopicAssetRow)
    group_ids, topic_ids, asset_ids = ({row.id for row in rows} for rows in [groups, topics, assets])
    if len({t.catalog_number for t in topics}) != len(topics):
        raise ValueError("Duplicate topic catalog number")
    if len({a.path for a in assets}) != len(assets):
        raise ValueError("Duplicate asset path")
    for row in topics:
        if row.group_id not in group_ids:
            raise ValueError(f"Unknown group {row.group_id}")
    for row in links:
        if row.topic_id not in topic_ids or row.asset_id not in asset_ids:
            raise ValueError(f"Broken topic-asset relationship: {row.topic_id}/{row.asset_id}")
    for row in assets:
        path = resolve_asset_path(dataset, row.path)
        digest = hashlib.sha256()
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(chunk)
        if path.stat().st_size != row.size_bytes or digest.hexdigest() != row.sha256:
            raise ValueError(f"Photo size or SHA-256 mismatch: {row.original_filename}")
    for model, rows in [(Group, groups), (Topic, topics), (Asset, assets), (TopicAsset, links)]:
        for row in rows:
            session.merge(model(**row.model_dump()))
        session.flush()
    return {"groups": len(groups), "topics": len(topics), "assets": len(assets), "topic_assets": len(links)}
