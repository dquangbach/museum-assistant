"""Export editable OCR documents and a per-topic review checklist; never overwrite edits."""
import argparse,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--topic')
    args=parser.parse_args()
    data=ROOT/'Dataset'
    documents=json.loads((data/'ocr/draft_documents.json').read_text())
    queue=json.loads((data/'ocr/review_queue.json').read_text())
    topics=json.loads((data/'metadata/topics.json').read_text())
    count=0
    for doc in documents:
        if args.topic and args.topic not in doc['topic_ids']:continue
        # Shared image has one editable document even when linked to two topics.
        path=data/'review/documents'/f"{doc['document_id']}.json"
        path.parent.mkdir(parents=True,exist_ok=True)
        if not path.exists():
            path.write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
            count+=1
    for topic in topics:
        if args.topic and args.topic!=topic['id']:continue
        lines=[f"# {topic['id']} — {topic['title']}", '',
               'OCR thô, chưa xác minh. Đối chiếu với ảnh trước khi duyệt.', '',
               'Một ảnh có thể không có chữ hoặc chứa nhiều bảng/nhãn. Không tự coi ảnh là hiện vật.', '']
        for item in queue:
            if topic['id'] not in item['topic_ids']:continue
            lines += [f"## {item['filename']}",f"- Asset ID: `{item['asset_id']}`",
                      f"- OCR: {item['ocr_status']}; {item['characters']} ký tự.",
                      f"- Ảnh nguồn: `{(data/item['source_path']).resolve()}`",
                      f"- Đã có tài liệu được duyệt: {item['already_has_verified_document']}."]
            edit=data/'review/documents'/f"{item['document_id']}.json"
            if edit.exists():lines.append(f"- Bản chỉnh sửa: `{edit.resolve()}`")
            else:lines.append('- Không có bản nháp riêng; xem ảnh và bản OCR gốc nếu cần.')
            lines.append('')
        output=data/'review/topics'/f"{topic['id']}.md"
        output.parent.mkdir(parents=True,exist_ok=True)
        output.write_text('\n'.join(lines),encoding='utf-8')
    print(f'Created {count} editable files; existing edits preserved.')


if __name__=='__main__':main()
