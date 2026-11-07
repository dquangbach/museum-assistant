import hashlib
import json
from pathlib import Path

from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
import pytest
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.db.session import make_engine
from app.main import create_app
from app.services.import_dataset import import_dataset


@pytest.fixture
def context(tmp_path, monkeypatch):
    dataset = tmp_path / "Dataset"
    metadata = dataset / "metadata"
    metadata.mkdir(parents=True)
    assets = []
    for index, classification in [(1, "shared"), (2, "unassigned")]:
        filename = f"IMG_{index}.JPG"
        photo = dataset / filename
        photo.write_bytes(f"test-photo-{index}".encode())
        assets.append({"id": f"asset-{index}", "original_filename": filename, "path": filename,
                       "media_type": "image/jpeg", "size_bytes": photo.stat().st_size,
                       "sha256": hashlib.sha256(photo.read_bytes()).hexdigest(), "asset_role": "unclassified",
                       "review_status": "needs_review", "classification_status": classification})
    rows = {
        "groups": [{"id": "GROUP01", "title": "Nhóm thử nghiệm", "sort_order": 1, "directory": "group"}],
        "topics": [{"id": f"TOPIC00{i}", "group_id": "GROUP01", "catalog_number": i,
                    "title": f"Chủ đề {i}", "summary": "Mô tả", "materials_notes": "Cần đối chiếu",
                    "source_reference": "1", "review_status": "needs_review", "directory": f"topic-{i}"} for i in [1, 2]],
        "assets": assets,
        "topic_assets": [{"topic_id": f"TOPIC00{i}", "asset_id": "asset-1", "sort_order": 1,
                          "assignment_source": "catalog.md", "review_status": "needs_review"} for i in [1, 2]],
    }
    for name, value in rows.items():
        (metadata / f"{name}.json").write_text(json.dumps(value), encoding="utf-8")
    database_url = f"sqlite:///{tmp_path / 'test.db'}"
    monkeypatch.setenv("DATABASE_URL", database_url)
    get_settings.cache_clear()
    config = Config(str(Path(__file__).resolve().parents[1] / "alembic.ini"))
    command.upgrade(config, "head")
    engine = make_engine(database_url)
    with Session(engine) as session, session.begin():
        import_dataset(session, dataset)
    settings = Settings(_env_file=None, database_url=database_url, dataset_dir=dataset, admin_api_key="test-admin-key")
    with TestClient(create_app(settings)) as client:
        yield {"client": client, "engine": engine, "dataset": dataset, "rows": rows, "settings": settings}
    engine.dispose()
    get_settings.cache_clear()
