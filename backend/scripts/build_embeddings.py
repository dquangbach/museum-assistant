"""Build verified vectors. Existing indices require explicit --force."""
import argparse
import json
import os
import tempfile
from pathlib import Path

from app.services.rag.dut_client import DUTClient, ROOT, MODEL, DIMENSIONS
from app.services.rag.vector_retrieval import digest, verified_documents


def build_index(source, output, client, batch_size=8, force=False, review=False):
    source, output = Path(source), Path(output)
    if not 1 <= batch_size <= 32:
        raise ValueError("batch_size phải từ 1 đến 32.")
    if output.exists() and not force:
        raise ValueError("Chỉ mục đã tồn tại. Chỉ dùng --force khi muốn tạo lại.")
    raw = source.read_bytes()
    chunks = verified_documents(raw, include_drafts=review)
    if not chunks:
        raise ValueError("Không có đoạn đã xác minh.")
    # Resume completed batches after an interrupted API call.
    cache_path = output.with_suffix(".cache.json")
    cache = {}
    if cache_path.exists():
        saved = json.loads(cache_path.read_text(encoding="utf-8"))
        if saved.get("model") == MODEL:
            cache = saved.get("vectors", {})
    records = []
    for start in range(0, len(chunks), batch_size):
        batch = chunks[start:start+batch_size]
        texts = [c["text"].strip() for c in batch]
        hashes = [digest(text.encode("utf-8")) for text in texts]
        missing = list(dict.fromkeys(h for h in hashes if h not in cache))
        if missing:
            text_by_hash = dict(zip(hashes, texts))
            fresh = client.embed([text_by_hash[h] for h in missing])
            if len(fresh) != len(missing):
                raise ValueError("Số vector không khớp batch.")
            cache.update(zip(missing, fresh))
            cache_tmp = cache_path.with_suffix(".tmp")
            cache_tmp.write_text(json.dumps({"model": MODEL, "vectors": cache},
                                           allow_nan=False), encoding="utf-8")
            cache_tmp.replace(cache_path)
        from app.services.rag.dut_client import normalize
        vectors = [normalize(cache[h]) for h in hashes]
        print(f"Embedding: {min(start+batch_size, len(chunks))}/{len(chunks)}", flush=True)
        for chunk, text, vector in zip(batch, texts, vectors):
            records.append({"chunk_id": chunk["chunk_id"],
                            "text_sha256": digest(text.encode("utf-8")),
                            "embedding": vector})
    if source.read_bytes() != raw:
        raise ValueError("Nguồn đã thay đổi trong lúc tạo embedding.")
    index = {"model": MODEL, "dimensions": DIMENSIONS, "normalized": True,
             "embedded_field": "text.strip()", "source_file": str(source.name), "scope": "review" if review else "verified",
             "source_sha256": digest(raw), "records": records}
    serialized = json.dumps(index, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
    output.parent.mkdir(parents=True, exist_ok=True)
    # Same-directory temporary file: failed writes never replace a valid index.
    fd, temporary = tempfile.mkstemp(dir=output.parent, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            stream.write(serialized)
        if force:
            os.replace(temporary, output)
        else:
            os.link(temporary, output)  # Atomic create, fails if destination exists.
    finally:
        Path(temporary).unlink(missing_ok=True)
    return len(records)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--review", action="store_true", help="Tạo chỉ mục OCR toàn bộ, tách khỏi kho đã duyệt")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--batch-size", type=int, default=8)
    args = parser.parse_args()
    try:
        source = "review_chunks.json" if args.review else "chunks.json"
        target = "review_embeddings.json" if args.review else "verified_embeddings.json"
        count = build_index(ROOT/"Dataset/processed"/source,
                            ROOT/"Dataset/processed"/target,
                            DUTClient.from_env(), args.batch_size, args.force, args.review)
        print(f"Đã lưu {count} vector, mỗi vector {DIMENSIONS} chiều.")
    except (ValueError, RuntimeError, OSError) as error:
        raise SystemExit(str(error)) from None


if __name__ == "__main__":
    main()
