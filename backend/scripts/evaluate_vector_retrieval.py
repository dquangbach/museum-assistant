"""Compare keyword, embedding and reranking on the same labeled questions."""
import argparse
import json
from datetime import datetime, timezone

from app.services.rag.dut_client import DUTClient, ROOT
from app.services.rag.retrieval import search_chunks
from app.services.rag.vector_retrieval import VectorRetriever


def evaluate(retriever, questions, candidate_k=20):
    if candidate_k < 3:
        raise ValueError("candidate-k phải >= 3 để đánh giá Hit@3.")
    available = {c["chunk_id"] for c in retriever.chunks}
    seen = set()
    for q in questions:
        expected = set(q["expected_chunk_ids"])
        if q["id"] in seen or type(q["answerable"]) is not bool or not q["question"].strip():
            raise ValueError("Câu hỏi trùng mã hoặc nhãn/nội dung không hợp lệ.")
        seen.add(q["id"])
        if (q["answerable"] and not expected) or expected - available:
            raise ValueError(f"{q['id']}: expected_chunk_ids không hợp lệ.")
        if not q["answerable"] and expected:
            raise ValueError(f"{q['id']}: câu không có đáp án không được có expected IDs.")
        eligible = {c["chunk_id"] for c in retriever.chunks if not q.get("topic_id")
                    or q["topic_id"] in (c.get("topic_ids") or [c.get("topic_id")])}
        if expected - eligible:
            raise ValueError(f"{q['id']}: đáp án nằm ngoài topic được lọc.")
    stats = {name: {"hit_at_1": 0, "hit_at_3": 0}
             for name in ("keyword", "embedding", "reranking")}
    details, total = [], 0
    for q in questions:
        text, topic = q["question"], q.get("topic_id")
        candidates = retriever.retrieve(text, topic, candidate_k)
        reranked = retriever.rerank(text, candidates, 3)
        keyword = search_chunks(text, retriever.chunks, topic_id=topic, top_k=3)
        results = {name: [r["chunk"]["chunk_id"] for r in rows]
                   for name, rows in (("keyword", keyword),
                                      ("embedding", candidates[:3]),
                                      ("reranking", reranked))}
        print(f"\n{q['id']}: {text}", flush=True)
        for name, ids in results.items():
            print(name, ids)
        if q["answerable"]:
            total += 1
            expected = set(q["expected_chunk_ids"])
            for name, ids in results.items():
                stats[name]["hit_at_1"] += int(bool(ids) and ids[0] in expected)
                stats[name]["hit_at_3"] += int(bool(expected.intersection(ids[:3])))
        else:
            print("Nhãn: không có đáp án; kết quả liên quan không chứng minh có thể trả lời.")
        details.append({**q, "results": results,
                        "embedding_candidates": [{"chunk_id": r["chunk"]["chunk_id"], "score": r["score"]} for r in candidates],
                        "reranking_scores": [{"chunk_id": r["chunk"]["chunk_id"], "score": r["score"]} for r in reranked]})
    return {"answerable_count": total, "question_count": len(questions),
            "stats": stats, "details": details, "candidate_limit": candidate_k}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate-k", type=int, default=20)
    parser.add_argument("--review", action="store_true")
    args = parser.parse_args()
    try:
        source = "review_chunks.json" if args.review else "chunks.json"
        target = "review_embeddings.json" if args.review else "verified_embeddings.json"
        retriever = VectorRetriever(ROOT/"Dataset/processed"/source,
            ROOT/"Dataset/processed"/target, DUTClient.from_env(), review=args.review)
        if args.review:
            print("THỬ NGHIỆM TOÀN KHO: nhãn kiểm thử cũ chưa được duyệt lại trên OCR; không đo khả năng từ chối.")
        questions = json.loads((ROOT/"Dataset/evaluation/questions.json").read_text(encoding="utf-8"))
        report = evaluate(retriever, questions, args.candidate_k)
        now = datetime.now(timezone.utc)
        report.update(created_at=now.isoformat(), source_sha256=retriever.index["source_sha256"],
                      embedding_model=retriever.index["model"],
                      scope="review" if args.review else "verified")
        output = ROOT/"Dataset/evaluation"/f"retrieval_comparison_{now.strftime('%Y%m%dT%H%M%S%fZ')}.json"
        with output.open("x", encoding="utf-8") as stream:
            json.dump(report, stream, ensure_ascii=False, indent=2, allow_nan=False)
            stream.write("\n")
        print("\n--- TỔNG KẾT ---")
        n = report["answerable_count"]
        for name, metrics in report["stats"].items():
            print(name)
            for metric, hits in metrics.items():
                print(f"  {metric}: {hits}/{n}" + (f" ({hits/n:.1%})" if n else " (N/A)"))
        print("Đã lưu:", output)
    except (ValueError, RuntimeError, OSError, KeyError) as error:
        raise SystemExit(str(error)) from None


if __name__ == "__main__":
    main()
