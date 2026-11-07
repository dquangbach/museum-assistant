import json

from fastapi.testclient import TestClient
import pytest
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.main import create_app
from app.models.catalog import Asset, Group, TopicAsset
from app.services.import_dataset import import_dataset
from app.services.media import resolve_asset_path


def test_catalog_pagination_shared_and_unassigned(context):
    client = context["client"]
    assert client.get("/health/ready").status_code == 200
    assert len(client.get("/api/v1/groups").json()) == 1
    page = client.get("/api/v1/topics?limit=1&offset=1&group_id=GROUP01").json()
    assert page["total"] == 2
    assert [item["id"] for item in page["items"]] == ["TOPIC002"]
    assert client.get("/api/v1/topics?q=khong-co").json()["total"] == 0
    assert client.get("/api/v1/topics?limit=0").status_code == 422
    for identifier in ["TOPIC001", "TOPIC002"]:
        result = client.get(f"/api/v1/topics/{identifier}/assets").json()
        assert result["items"][0]["id"] == "asset-1"
    assert client.get("/api/v1/assets?classification_status=unassigned").json()["items"][0]["id"] == "asset-2"
    assert client.get("/api/v1/topics/missing/assets").status_code == 404
    assert client.get("/api/v1/assets/asset-1").json()["file_url"] == "/api/v1/assets/asset-1/file"


def test_import_is_idempotent(context):
    with Session(context["engine"]) as session, session.begin():
        counts = import_dataset(session, context["dataset"])
        assert counts == {"groups": 1, "topics": 2, "assets": 2, "topic_assets": 2}
    with Session(context["engine"]) as session:
        assert session.scalar(select(func.count()).select_from(Asset)) == 2
        assert session.scalar(select(func.count()).select_from(TopicAsset)) == 2


def test_invalid_import_does_not_change_database(context):
    metadata = context["dataset"] / "metadata"
    groups = context["rows"]["groups"]
    groups[0]["title"] = "Should not be committed"
    (metadata / "groups.json").write_text(json.dumps(groups))
    links = context["rows"]["topic_assets"]
    links[0]["asset_id"] = "missing"
    (metadata / "topic_assets.json").write_text(json.dumps(links))
    with pytest.raises(ValueError, match="Broken topic-asset"):
        with Session(context["engine"]) as session, session.begin():
            import_dataset(session, context["dataset"])
    with Session(context["engine"]) as session:
        assert session.get(Group, "GROUP01").title == "Nhóm thử nghiệm"


def test_import_detects_changed_photo(context):
    (context["dataset"] / "IMG_1.JPG").write_bytes(b"changed")
    with pytest.raises(ValueError, match="SHA-256 mismatch"):
        with Session(context["engine"]) as session, session.begin():
            import_dataset(session, context["dataset"])


def test_admin_publish_qr_and_patch_validation(context):
    client = context["client"]
    headers = {"X-Admin-Key": "test-admin-key"}
    payload = {"id": "EX001", "topic_id": "TOPIC001", "name": "Hiện vật thử nghiệm",
               "description": "Dữ liệu dành riêng cho kiểm thử", "asset_ids": ["asset-1"]}
    assert client.post("/api/v1/admin/exhibits", json=payload).status_code == 401
    assert client.post("/api/v1/admin/exhibits", json={**payload, "is_published": True}, headers=headers).status_code == 422
    assert client.post("/api/v1/admin/exhibits", json={**payload, "asset_ids": ["missing"]}, headers=headers).status_code == 422
    created = client.post("/api/v1/admin/exhibits", json=payload, headers=headers)
    assert created.status_code == 201
    assert created.json()["assets"][0]["id"] == "asset-1"
    assert client.post("/api/v1/admin/exhibits", json=payload, headers=headers).status_code == 409
    assert client.get("/api/v1/exhibits/EX001").status_code == 404
    assert client.get("/api/v1/exhibits").json()["total"] == 0
    assert client.get("/api/v1/qr/resolve", params={"value": "museum://exhibit/EX001"}).status_code == 404
    updated = client.patch("/api/v1/admin/exhibits/EX001", json={"review_status": "verified", "is_published": True}, headers=headers)
    assert updated.status_code == 200
    assert updated.json()["assets"][0]["id"] == "asset-1"
    assert client.get("/api/v1/exhibits?topic_id=TOPIC001").json()["total"] == 1
    assert client.get("/api/v1/exhibits/EX001").json()["qr_payload"] == "museum://exhibit/EX001"
    assert client.get("/api/v1/qr/resolve", params={"value": "museum-demo://exhibit/ex001"}).json()["id"] == "EX001"
    assert client.patch("/api/v1/admin/exhibits/EX001", json={"name": None}, headers=headers).status_code == 422
    assert client.patch("/api/v1/admin/exhibits/EX001", json={"review_status": "needs_review"}, headers=headers).status_code == 422
    assert client.get("/api/v1/exhibits/EX001").json()["name"] == payload["name"]
    assert client.get("/api/v1/admin/exhibits", headers=headers).json()["total"] == 1
    assert client.patch("/api/v1/admin/exhibits/EX001", json={"is_published": False}, headers=headers).status_code == 200
    assert client.get("/api/v1/exhibits/EX001").status_code == 404


def test_qr_invalid_and_topic(context):
    client = context["client"]
    assert client.get("/api/v1/qr/resolve", params={"value": "museum://topic/TOPIC001"}).json()["detail_url"] == "/api/v1/topics/TOPIC001"
    for value in ["https://example.com/exhibit/EX001", "museum://topic/TOPIC001?x=1", "museum://topic/../EX001", "museum://checkpoint/CP01"]:
        assert client.get("/api/v1/qr/resolve", params={"value": value}).status_code == 400
    assert client.get("/api/v1/qr/resolve", params={"value": "museum://topic/MISSING"}).status_code == 404


def test_media_file_and_escape_protection(context, tmp_path):
    client = context["client"]
    response = client.get("/api/v1/assets/asset-1/file")
    assert response.status_code == 200
    assert response.content == b"test-photo-1"
    assert response.headers["content-type"] == "image/jpeg"
    secret = tmp_path / "secret.JPG"
    secret.write_bytes(b"outside Dataset")
    with Session(context["engine"]) as session, session.begin():
        session.get(Asset, "asset-1").path = "../secret.JPG"
    assert client.get("/api/v1/assets/asset-1/file").status_code == 404
    with pytest.raises(ValueError):
        resolve_asset_path(context["dataset"], str(secret))
    symlink = context["dataset"] / "linked.JPG"
    symlink.symlink_to(secret)
    with pytest.raises(ValueError):
        resolve_asset_path(context["dataset"], "linked.JPG")


def test_disabled_admin(context):
    context["settings"].admin_api_key = ""
    assert context["client"].get("/api/v1/admin/exhibits").status_code == 503


def test_readiness_requires_migrations(tmp_path):
    settings = Settings(_env_file=None, database_url=f"sqlite:///{tmp_path / 'empty.db'}", dataset_dir=tmp_path)
    with TestClient(create_app(settings)) as client:
        assert client.get("/health/live").status_code == 200
        assert client.get("/health/ready").status_code == 503
