import json
from pathlib import Path

from app.services.rag.retrieval import search_chunks


def main() -> None:
    project_root = Path(__file__).resolve().parents[2]

    chunks_path = project_root / "Dataset/processed/chunks.json"
    questions_path = project_root / "Dataset/evaluation/questions.json"

    chunks = json.loads(chunks_path.read_text(encoding="utf-8"))
    questions = json.loads(questions_path.read_text(encoding="utf-8"))

    available_ids = {chunk["chunk_id"] for chunk in chunks}

    total_answerable = 0
    hit_at_1 = 0
    hit_at_3 = 0

    for question in questions:
        expected_ids = set(question["expected_chunk_ids"])

        if question["answerable"] and not expected_ids:
            raise ValueError(
                f"{question['id']}: câu có đáp án phải có expected_chunk_ids."
            )

        unknown_ids = expected_ids - available_ids
        if unknown_ids:
            raise ValueError(
                f"{question['id']}: mã đoạn không tồn tại: "
                f"{sorted(unknown_ids)}"
            )

        results = search_chunks(
            question=question["question"],
            chunks=chunks,
            topic_id=question.get("topic_id"),
            top_k=3,
        )

        retrieved_ids = [
            result["chunk"]["chunk_id"]
            for result in results
        ]

        print(f"\n{question['id']}: {question['question']}")
        print("Kết quả:", retrieved_ids or "Không tìm thấy")

        if not question["answerable"]:
            print(
                "Không có đáp án trong kho tư liệu. "
                "Kết quả tìm kiếm chỉ là các đoạn liên quan, "
                "không chứng minh có thể trả lời."
            )
            continue

        total_answerable += 1

        top_1_correct = bool(
            retrieved_ids and retrieved_ids[0] in expected_ids
        )
        top_3_correct = bool(expected_ids & set(retrieved_ids))

        hit_at_1 += int(top_1_correct)
        hit_at_3 += int(top_3_correct)

        print("Đoạn mong đợi:", sorted(expected_ids))
        print("Đúng ở vị trí đầu:", "CÓ" if top_1_correct else "KHÔNG")
        print("Có trong 3 kết quả:", "CÓ" if top_3_correct else "KHÔNG")

    print("\n--- TỔNG KẾT ---")

    if total_answerable == 0:
        print("Chưa có câu hỏi có đáp án để tính kết quả.")
        return

    print(f"Số câu có đáp án: {total_answerable}")
    print(
        f"Hit@1: {hit_at_1}/{total_answerable} "
        f"({hit_at_1 / total_answerable:.0%})"
    )
    print(
        f"Hit@3: {hit_at_3}/{total_answerable} "
        f"({hit_at_3 / total_answerable:.0%})"
    )


if __name__ == "__main__":
    main()