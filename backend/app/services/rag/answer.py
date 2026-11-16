"""Grounded answers from verified museum documents only."""
import json
from pathlib import Path

from app.services.rag.retrieval import search_chunks

NO_EVIDENCE = "Chưa có đủ tư liệu đã xác minh để trả lời câu hỏi này."


def verified_chunks(dataset_dir: Path) -> list[dict]:
    path = dataset_dir / "processed" / "chunks.json"
    if not path.is_file():
        return []
    rows = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(rows, list):
        raise ValueError("Verified knowledge index is invalid")
    return [row for row in rows if row.get("review_status") == "verified"]


def answer_question(question: str, topic_id: str | None, dataset_dir: Path,
                    api_key: str, model: str, generator=None) -> dict:
    matches = search_chunks(question, verified_chunks(dataset_dir), topic_id=topic_id, top_k=3)
    if not matches:
        return {"answer": NO_EVIDENCE, "answered": False, "sources": []}

    sources = []
    passages = []
    for match in matches:
        chunk = match["chunk"]
        sources.append({
            "chunk_id": chunk["chunk_id"],
            "topic_id": chunk["topic_id"],
            "title": chunk["title"],
            "image_urls": [f"/api/v1/assets/{asset_id}/file" for asset_id in chunk["source_asset_ids"]],
            "image_names": chunk["source_filenames"],
        })
        passages.append(f"[{chunk['chunk_id']}] {chunk['title']}\n{chunk['text']}")

    if generator is None:
        from google import genai
        client = genai.Client(api_key=api_key)
        generator = lambda prompt: client.models.generate_content(model=model, contents=prompt).text

    prompt = (
        "Bạn là trợ lý Bảo tàng Đà Nẵng. Chỉ dùng các đoạn tư liệu sau để trả lời bằng tiếng Việt. "
        "Nếu các đoạn không chứa đáp án rõ ràng, trả đúng câu: " + NO_EVIDENCE + " "
        "Không đoán, không thêm sự kiện hay nguồn ngoài tư liệu. Trả lời ngắn gọn.\n\n"
        f"Câu hỏi: {question}\n\nTư liệu đã xác minh:\n" + "\n\n".join(passages)
    )
    answer = (generator(prompt) or "").strip()
    if not answer or answer == NO_EVIDENCE:
        return {"answer": NO_EVIDENCE, "answered": False, "sources": []}
    return {"answer": answer, "answered": True, "sources": sources}
