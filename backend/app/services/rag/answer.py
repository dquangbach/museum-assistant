"""Generate grounded answers using verified DUT AI retrieval and Gemini."""
from pathlib import Path

from app.services.rag.dut_client import DUTClient
from app.services.rag.vector_retrieval import VectorRetriever

NO_EVIDENCE = "Chưa có đủ tư liệu đã xác minh để trả lời câu hỏi này."


def answer_question(question: str, topic_id: str | None, dataset_dir: Path,
                    api_key: str, model: str, generator=None,
                    dut_client=None) -> dict:
    """Retrieve only verified chunks, rerank them, then generate with Gemini.

    Inject generator and dut_client in tests to avoid external API calls.
    """
    client = dut_client or DUTClient.from_env()
    chunks_path = dataset_dir / "processed" / "chunks.json"
    index_path = dataset_dir / "processed" / "verified_embeddings.json"
    retriever = VectorRetriever(chunks_path, index_path, client)
    candidates = retriever.retrieve(question, topic_id=topic_id, candidate_k=20)
    if not candidates:
        return {"answer": NO_EVIDENCE, "answered": False, "sources": []}
    matches = retriever.rerank(question, candidates, top_k=min(3, len(candidates)))
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
            "image_urls": [f"/api/v1/assets/{asset_id}/file" for asset_id in chunk.get("source_asset_ids", [])],
            "image_names": chunk.get("source_filenames", []),
            "review_status": chunk.get("review_status", "unknown"),
        })
        passages.append(f"[{chunk['chunk_id']}] {chunk['title']}\n{chunk['text']}")

    if generator is None:
        if not api_key:
            raise ValueError("Thiếu GEMINI_API_KEY trên backend.")
        from google import genai
        client = genai.Client(api_key=api_key)
        generator = lambda prompt: client.models.generate_content(
            model=model, contents=prompt
        ).text

    prompt = (
        "Bạn là trợ lý Bảo tàng Đà Nẵng. Trả lời bằng tiếng Việt, ngắn gọn. "
        "Chỉ dùng thông tin trong tư liệu được cung cấp; không dùng kiến thức bên ngoài. "
        "Nếu tư liệu không nêu rõ câu trả lời, hãy trả đúng câu: " + NO_EVIDENCE + "\n"
        "Ghi mã đoạn nguồn trong câu trả lời, ví dụ [DOC001_v1_001].\n\n"
        f"Câu hỏi: {question}\n\nTư liệu đã xác minh:\n" + "\n\n".join(passages)
    )
    answer = (generator(prompt) or "").strip()
    if not answer or answer == NO_EVIDENCE:
        return {"answer": NO_EVIDENCE, "answered": False, "sources": []}
    return {"answer": answer, "answered": True, "sources": sources}
