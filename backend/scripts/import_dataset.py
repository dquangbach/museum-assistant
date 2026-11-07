"""Run from backend/: python -m scripts.import_dataset"""
import argparse
import json
from pathlib import Path

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.session import make_engine
from app.services.import_dataset import import_dataset


def main():
    parser = argparse.ArgumentParser(description="Validate and import Dataset metadata and photo references")
    parser.add_argument("--dataset", type=Path, default=get_settings().dataset_dir)
    args = parser.parse_args()
    engine = make_engine(get_settings().database_url)
    try:
        with Session(engine) as session, session.begin():
            result = import_dataset(session, args.dataset)
        print(json.dumps({"imported": result}, ensure_ascii=False))
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
