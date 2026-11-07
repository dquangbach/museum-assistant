from pathlib import Path


def resolve_asset_path(root: Path, relative_path: str) -> Path:
    root = root.resolve()
    relative = Path(relative_path)
    if relative.is_absolute() or ".." in relative.parts:
        raise ValueError("Asset path must be relative to Dataset")
    path = (root / relative).resolve()
    if not path.is_relative_to(root):
        raise ValueError("Asset path escapes Dataset")
    if not path.is_file():
        raise FileNotFoundError(relative_path)
    if path.suffix.lower() not in {".jpg", ".jpeg", ".png", ".webp", ".heic"}:
        raise ValueError("Unsupported asset file")
    return path
