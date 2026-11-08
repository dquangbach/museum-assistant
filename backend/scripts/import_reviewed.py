"""Import a manually corrected, explicitly verified document into curated data."""
import argparse,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]


def validate(doc, assets, topics, links):
    if doc.get('review_status')!='verified':raise ValueError('Set verified only after checking the source photo.')
    if doc.get('language') not in {'vi','en'}:raise ValueError('Set language vi or en; split bilingual text into separate documents.')
    if not doc.get('title','').strip() or not doc.get('text','').strip():raise ValueError('Missing title/text')
    if not doc.get('review_notes','').strip():raise ValueError('Document the review in review_notes')
    if '[không đọc rõ]' in doc['text'].lower():raise ValueError('Unresolved unreadable text')
    tids=doc.get('topic_ids') or [doc.get('topic_id')]
    if doc.get('topic_id') not in tids or any(t not in topics for t in tids):raise ValueError('Invalid topic mapping')
    if not isinstance(doc.get('version'),int) or doc['version']<1:raise ValueError('Invalid version')
    ids=doc.get('source_asset_ids',[])
    if not ids or any(a not in assets for a in ids):raise ValueError('Invalid source assets')
    if doc.get('source_filenames')!=[assets[a]['original_filename'] for a in ids]:raise ValueError('Source filenames do not match IDs')
    if any(not any((t,a) in links for a in ids) for t in tids):raise ValueError('Topic not linked to source photo; review metadata first')
    return doc


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('file',type=Path)
    args=parser.parse_args()
    data=ROOT/'Dataset'
    load=lambda name:json.loads((data/'metadata'/f'{name}.json').read_text())
    doc=json.loads(args.file.read_text())
    validate(doc,{a['id']:a for a in load('assets')},{t['id'] for t in load('topics')},
             {(r['topic_id'],r['asset_id']) for r in load('topic_assets')})
    curated=data/'curated/documents.json'
    documents=json.loads(curated.read_text())
    index=next((i for i,d in enumerate(documents) if d['document_id']==doc['document_id']),None)
    if index is None:documents.append(doc)
    elif documents[index]==doc:
        print('Already imported; no changes.');return
    elif doc['version']<=documents[index]['version']:
        raise ValueError('Increment version before replacing an existing document')
    else:documents[index]=doc
    temp=curated.with_suffix('.tmp')
    temp.write_text(json.dumps(documents,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    temp.replace(curated)
    print('Imported:',doc['document_id'],'; rebuild ingestion and review index.')


if __name__=='__main__':main()
