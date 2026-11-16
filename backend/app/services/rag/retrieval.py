import argparse
import json
import re
import unicodedata
from pathlib import Path


STOP_WORDS = {
    "là", "gì", "của", "và", "có", "ở", "được",
    "những", "các", "một", "nào", "cho", "về",
}


def tokenize(text: str) -> set[str]:
    """Chuyển văn bản thành tập từ để so khớp."""
    text = unicodedata.normalize("NFC", text.lower())
    words = re.findall(r"\w+", text, flags=re.UNICODE)

    return {
        word
        for word in words
        if word not in STOP_WORDS
    }


def search_chunks(
    question: str,
    chunks: list[dict],
    topic_id: str | None = None,
    top_k: int = 3,
) -> list[dict]:
    """Xếp hạng đoạn theo số từ trùng với câu hỏi."""
    query_words = tokenize(question)

    if not query_words or top_k <= 0:
        return []

    results = []

    for chunk in chunks:
        # Nếu chọn chủ đề, chỉ tìm trong chủ đề đó.
        if topic_id and topic_id not in (chunk.get("topic_ids") or [chunk.get("topic_id")]):
            continue

        content_words = tokenize(chunk["text"])

        matched_content = query_words & content_words
        # Metadata danh mục ngắn: cho phép tìm theo tên chủ đề.
        # Giữ nguyên baseline kho tài liệu đã duyệt để so sánh đánh giá cũ.
        matched_title = (query_words & tokenize(chunk['title'])
                         if chunk.get('source_type') == 'catalog_metadata' else set())
        score = len(matched_content) + len(matched_title)
        matched_words = matched_content | matched_title

        if score == 0:
            continue

        results.append(
            {
                "chunk": chunk,
                "score": score,
                "matched_words": sorted(matched_words),
            }
        )

    results.sort(
        key=lambda item: (
            -item["score"],
            item["chunk"]["chunk_id"],
        )
    )

    return results[:top_k]


def main() -> None:
    parser = argparse.ArgumentParser(description="Tìm tư liệu trên mọi chủ đề hoặc lọc theo topic.")
    parser.add_argument('--topic', help='Ví dụ TOPIC005; bỏ trống để tìm toàn bộ')
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--review', action='store_true', help='Tìm trong bản nháp OCR CHƯA XÁC MINH')
    mode.add_argument('--catalog', action='store_true', help='Tìm trong metadata 38 chủ đề CHƯA XÁC MINH')
    parser.add_argument('--query', help='Hỏi một câu rồi thoát')
    parser.add_argument('--top-k', type=int, default=3)
    args = parser.parse_args()
    if args.top_k < 1:
        parser.error('--top-k phải >= 1')
    root = Path(__file__).resolve().parents[4]
    filename = 'catalog_chunks.json' if args.catalog else 'review_chunks.json' if args.review else 'chunks.json'
    path = root / 'Dataset/processed' / filename
    if not path.exists():
        raise SystemExit('Chạy ingestion trước với cùng chế độ --catalog hoặc --review.')
    chunks = json.loads(path.read_text(encoding='utf-8'))
    if args.topic and not any(args.topic in (c.get('topic_ids') or [c['topic_id']]) for c in chunks):
        raise SystemExit(f'Kho đang chọn chưa có đoạn nào cho {args.topic}.')
    print(f'Đã tải {len(chunks)} đoạn. Phạm vi: {args.topic or "tất cả chủ đề"}.')
    if args.review or args.catalog:
        print('CHẾ ĐỘ ĐỐI CHIẾU: nội dung chưa xác minh; không dùng làm câu trả lời chính thức.')
    while True:
        try:
            question = args.query if args.query is not None else input('\nCâu hỏi (exit để thoát): ').strip()
        except (EOFError, KeyboardInterrupt):
            break
        if question.lower() == 'exit':break
        if not question.strip():
            if args.query is not None:break
            continue
        results = search_chunks(question, chunks, topic_id=args.topic, top_k=args.top_k)
        if not results:print('Không tìm thấy từ khóa trùng; điều này không khẳng định kho không có đáp án.')
        for rank, result in enumerate(results, 1):
            chunk = result['chunk']
            print(f"\n--- Kết quả {rank} ---")
            print('Mã đoạn:', chunk['chunk_id'])
            print('Chủ đề:', ', '.join(chunk.get('topic_ids') or [chunk['topic_id']]))
            print('Tiêu đề:', chunk['title'])
            print('Trạng thái:', chunk.get('review_status', 'unknown'), chunk.get('ocr_status') or '')
            print('Điểm từ khóa:', result['score'])
            print('Nội dung:', chunk['text'])
            print('Ảnh nguồn:', ', '.join(chunk['source_filenames']))
        if args.query is not None:break


if __name__ == '__main__':
    main()
