"""Read-only integrity audit of generated knowledge files and source references."""
import json
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]


def main():
    data=ROOT/'Dataset'
    load=lambda path:json.loads((data/path).read_text(encoding='utf-8'))
    assets={a['id']:a for a in load('metadata/assets.json')}
    topics={t['id'] for t in load('metadata/topics.json')}
    links={(r['topic_id'],r['asset_id']) for r in load('metadata/topic_assets.json')}
    queue=load('ocr/review_queue.json')
    if len(queue)!=len(assets) or {q['asset_id'] for q in queue}!=set(assets):
        raise ValueError('Review queue does not cover every asset exactly once')
    for q in queue:
        record=load('ocr/records/'+q['asset_id']+'.json')
        if record['source_sha256']!=assets[q['asset_id']]['sha256']:
            raise ValueError('OCR/source hash mismatch')
    curated=load('curated/documents.json')
    drafts=load('ocr/draft_documents.json')
    for group in [curated,drafts]:
        if len({d['document_id'] for d in group})!=len(group):raise ValueError('Duplicate document IDs')
        for doc in group:
            ids=doc['source_asset_ids']
            if any(a not in assets for a in ids):raise ValueError('Unknown source asset')
            if doc['source_filenames']!=[assets[a]['original_filename'] for a in ids]:raise ValueError('Wrong filename')
            for t in doc.get('topic_ids') or ([doc['topic_id']] if doc.get('topic_id') else []):
                if t not in topics or not any((t,a) in links for a in ids):raise ValueError('Invalid topic reference')
    if any(d['review_status']!='needs_review' for d in drafts):raise ValueError('OCR unexpectedly marked verified')
    for name in ['chunks.json','review_chunks.json']:
        chunks=load('processed/'+name)
        if len({c['chunk_id'] for c in chunks})!=len(chunks):raise ValueError('Duplicate chunk IDs')
        if name=='chunks.json' and any(c['review_status']!='verified' for c in chunks):raise ValueError('Draft leaked into verified index')
        print(name,':',len(chunks),'chunks,',len({t for c in chunks for t in c['topic_ids']}),'topics')
    print('All source mappings and review boundaries passed.')
    print('OCR:',dict(Counter(q['ocr_status'] for q in queue)))
    print('Original evaluation questions are not expanded automatically.')


if __name__=='__main__':main()
