"""Verified-only vector retrieval, compatible with the existing JSON index."""
import argparse
import hashlib
import json
from pathlib import Path

from app.services.rag.dut_client import DUTClient, ROOT, MODEL, DIMENSIONS, normalize


def digest(data):
    return hashlib.sha256(data).hexdigest()


def verified_documents(raw, include_drafts=False):
    rows = json.loads(raw)
    if not isinstance(rows, list) or any(not isinstance(row, dict) for row in rows):
        raise ValueError("Kho tư liệu phải là danh sách các object.")
    chunks = [row for row in rows if row.get("review_status") == "verified" or include_drafts]
    ids = set()
    for row in chunks:
        cid, text = row.get("chunk_id"), row.get("text")
        if not isinstance(cid, str) or not cid or cid in ids or not isinstance(text, str) or not text.strip():
            raise ValueError("Đoạn thiếu mã/nội dung hoặc trùng mã.")
        ids.add(cid)
    return chunks


class VectorRetriever:
    def __init__(self, chunks_path, index_path, client, review=False):
        raw = Path(chunks_path).read_bytes()
        self.chunks = verified_documents(raw, include_drafts=review)
        self.index = json.loads(Path(index_path).read_text(encoding="utf-8"))
        if (self.index.get("scope", "verified") != ("review" if review else "verified")
                or self.index.get("model") != MODEL or self.index.get("dimensions") != DIMENSIONS
                or self.index.get("source_sha256") != digest(raw)
                or self.index.get("embedded_field") != "text.strip()"):
            raise ValueError("Chỉ mục cũ hoặc không tương thích; hãy tạo lại embedding.")
        by_id = {c["chunk_id"]: c for c in self.chunks}
        self.vectors = {}
        for row in self.index["records"]:
            cid = row["chunk_id"]
            if cid not in by_id or cid in self.vectors:
                raise ValueError("Mã đoạn trong chỉ mục không hợp lệ.")
            if row["text_sha256"] != digest(by_id[cid]["text"].strip().encode("utf-8")):
                raise ValueError("Nội dung không khớp vector.")
            self.vectors[cid] = normalize(row["embedding"])
        if set(self.vectors) != set(by_id) or not by_id:
            raise ValueError("Chỉ mục thiếu đoạn hoặc kho đã duyệt trống.")
        self.client = client

    def retrieve(self, question, topic_id=None, candidate_k=20):
        if candidate_k < 1:
            raise ValueError("candidate_k phải >= 1.")
        eligible = [c for c in self.chunks if not topic_id
                    or topic_id in (c.get("topic_ids") or [c.get("topic_id")])]
        if not question.strip() or not eligible:
            return []
        query = self.client.embed([question.strip()])[0]
        rows = [{"chunk": c, "score": sum(a*b for a, b in zip(query, self.vectors[c["chunk_id"]]))}
                for c in eligible]
        return sorted(rows, key=lambda r: (-r["score"], r["chunk"]["chunk_id"]))[:candidate_k]

    def rerank(self, question, candidates, top_k=3):
        if top_k < 1:
            raise ValueError("top_k phải >= 1.")
        rows = self.client.rerank(question, [c["chunk"]["text"].strip() for c in candidates])
        return [{"chunk": candidates[r["index"]]["chunk"], "score": r["score"],
                 "cosine": candidates[r["index"]]["score"]} for r in rows[:top_k]]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--review", action="store_true", help="Tìm toàn bộ OCR chưa duyệt, chỉ để thử nghiệm")
    parser.add_argument("--query", required=True)
    parser.add_argument("--topic")
    parser.add_argument("--candidate-k", type=int, default=20)
    parser.add_argument("--top-k", type=int, default=3)
    parser.add_argument("--no-rerank", action="store_true")
    args = parser.parse_args()
    if args.top_k < 1 or args.candidate_k < args.top_k:
        parser.error("Cần candidate-k >= top-k >= 1.")
    try:
        source = "review_chunks.json" if args.review else "chunks.json"
        target = "review_embeddings.json" if args.review else "verified_embeddings.json"
        retriever = VectorRetriever(ROOT/"Dataset/processed"/source,
            ROOT/"Dataset/processed"/target, DUTClient.from_env(), review=args.review)
        if args.review:
            print("THỬ NGHIỆM: chứa OCR chưa xác minh, không dùng làm câu trả lời chính thức.")
        candidates = retriever.retrieve(args.query, args.topic, args.candidate_k)
        results = candidates[:args.top_k] if args.no_rerank else retriever.rerank(args.query, candidates, args.top_k)
        for rank, result in enumerate(results, 1):
            c = result["chunk"]
            print(f"\n{rank}. {c['chunk_id']} | điểm: {result['score']:.6f}")
            print("Chủ đề:", ", ".join(c.get("topic_ids") or [c.get("topic_id", "")]))
            print("Trạng thái:", c.get("review_status"), c.get("ocr_status"))
            print(c["text"])
            print("Ảnh nguồn:", ", ".join(c.get("source_filenames", [])))
        print("Đây là kết quả truy xuất, không xác nhận câu hỏi có đủ đáp án.")
    except (ValueError, RuntimeError, OSError, KeyError) as error:
        raise SystemExit(str(error)) from None


if __name__ == "__main__":
    main()
