"""Build verified chunks by default, and an explicitly separate review index."""
import argparse
import json
import re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[4]


def load_documents(path: Path) -> list[dict]:
    documents = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(documents, list):
        raise ValueError('Documents must be a JSON list')
    seen = set()
    for doc in documents:
        key = doc['document_id']
        if key in seen:raise ValueError(f'Duplicate document_id: {key}')
        seen.add(key)
        if not doc['title'].strip() or not doc['text'].strip():
            raise ValueError(f'{key}: missing title/text')
        if not doc['source_asset_ids']:raise ValueError(f'{key}: missing source assets')
        if doc.get('review_status') not in {'verified','needs_review'}:
            raise ValueError(f'{key}: invalid review_status')
    return documents


def split_text(text, max_chars=1600):
    """Keep original paragraph boundaries and split long blocks at whitespace."""
    for paragraph in re.split(r'\n\s*\n',text.strip()):
        paragraph = paragraph.strip()
        while len(paragraph)>max_chars:
            cut = paragraph.rfind(' ',0,max_chars+1)
            if cut<1:cut=max_chars
            yield paragraph[:cut].strip()
            paragraph=paragraph[cut:].strip()
        if paragraph:yield paragraph


def ocr_search_text(text):
    """Remove very short OCR noise and group sparse lines for review search only.

    Raw text remains in the source document. This does not fix column order.
    """
    groups = []
    current = []
    size = 0
    for block in re.split(r"\n\s*\n", text.strip()):
        block = " ".join(block.split())
        if sum(c.isalpha() for c in block) < 6 or len(block.split()) < 2:
            continue
        if current and size + len(block) > 1100:
            groups.append(" ".join(current))
            current, size = [], 0
        current.append(block)
        size += len(block) + 1
    if current:
        groups.append(" ".join(current))
    return "\n\n".join(groups)


def build_chunks(documents: list[dict], include_drafts=False) -> list[dict]:
    chunks=[]
    for doc in documents:
        if doc.get('review_status')!='verified' and not include_drafts:continue
        tids=doc.get('topic_ids') or ([doc['topic_id']] if doc.get('topic_id') else [])
        # Unassigned photos stay in the review queue, not in retrieval.
        if not tids:continue
        text = ocr_search_text(doc['text']) if doc.get('ocr_status') and doc.get('review_status') != 'verified' else doc['text']
        for index,paragraph in enumerate(split_text(text),1):
            chunks.append({'chunk_id':f"{doc['document_id']}_v{doc['version']}_{index:03d}",
                           'document_id':doc['document_id'],'topic_id':doc.get('topic_id') or tids[0],
                           'topic_ids':tids,'exhibit_id':doc.get('exhibit_id'),'title':doc['title'],
                           'language':doc['language'],'text':paragraph,'source_asset_ids':doc['source_asset_ids'],
                           'source_filenames':doc['source_filenames'],'version':doc['version'],
                           'review_status':doc.get('review_status','needs_review'),
                           'ocr_status':doc.get('ocr_status')})
    return chunks


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--review',action='store_true',help='Build a separate unverified OCR review index')
    args=parser.parse_args()
    documents=load_documents(ROOT/'Dataset/curated/documents.json')
    if args.review:
        drafts=load_documents(ROOT/'Dataset/ocr/draft_documents.json')
        ids={d['document_id'] for d in documents}
        covered={a for d in documents if d.get('review_status')=='verified' for a in d['source_asset_ids']}
        documents += [d for d in drafts if d['document_id'] not in ids and not covered.intersection(d['source_asset_ids'])]
    chunks=build_chunks(documents,include_drafts=args.review)
    output=ROOT/'Dataset/processed'/('review_chunks.json' if args.review else 'chunks.json')
    output.parent.mkdir(parents=True,exist_ok=True)
    temp=output.with_suffix('.tmp')
    temp.write_text(json.dumps(chunks,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    temp.replace(output)
    print(f"Documents: {len(documents)}; chunks: {len(chunks)}; topics: {len({t for c in chunks for t in c['topic_ids']})}")
    print('REVIEW ONLY: contains unverified OCR' if args.review else 'VERIFIED DOCUMENTS ONLY')
    print(output)


if __name__=='__main__':main()
