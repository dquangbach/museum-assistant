"""OCR all museum photos locally; generated documents always need review."""
import argparse, csv, hashlib, io, json, os, shutil, subprocess, tempfile
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / 'Dataset'
CONFIG = {'languages': 'vie+eng', 'psm': 11, 'max_edge': 3200, 'version': 1}


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix('.tmp')
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    tmp.replace(path)


def parse_tsv(tsv):
    blocks, words = {}, []
    for row in csv.DictReader(io.StringIO(tsv), delimiter='\t', quoting=csv.QUOTE_NONE):
        text = (row.get('text') or '').strip()
        if row.get('level') != '5' or not text:
            continue
        key = (row['page_num'], row['block_num'], row['par_num'])
        blocks.setdefault(key, {}).setdefault(row['line_num'], []).append(text)
        words.append({'text': text, 'confidence': float(row['conf']),
                      'box': [int(row[k]) for k in ('left','top','width','height')]})
    return '\n\n'.join(' '.join(' '.join(tokens) for tokens in lines.values()) for lines in blocks.values()), words


def engine():
    local = ROOT / '.tools/tesseract'
    binary = local / 'usr/bin/tesseract'
    env = dict(os.environ, OMP_THREAD_LIMIT='1')
    if binary.exists():
        env['LD_LIBRARY_PATH'] = str(local/'usr/lib/x86_64-linux-gnu') + (':'+env['LD_LIBRARY_PATH'] if env.get('LD_LIBRARY_PATH') else '')
        env['TESSDATA_PREFIX'] = str(local/'usr/share/tesseract-ocr/5/tessdata')
        return str(binary), env
    binary = shutil.which('tesseract')
    if not binary:
        raise SystemExit('Install Tesseract with vie+eng language data first.')
    return binary, env


def process(asset, binary, env, force):
    from PIL import Image, ImageOps
    target = DATA/'ocr/records'/f"{asset['id']}.json"
    source = DATA/asset['path']
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    if digest != asset['sha256']:
        raise ValueError(f"Source checksum mismatch: {source}")
    if target.exists() and not force:
        old = json.loads(target.read_text())
        if old.get('config') == CONFIG and old.get('source_sha256') == digest and old.get('status') != 'error':
            return old
    record = {'asset_id':asset['id'], 'filename':asset['original_filename'], 'source_path':asset['path'],
              'source_sha256':digest, 'config':CONFIG, 'text':'', 'words':[], 'review_status':'needs_review'}
    try:
        with Image.open(source) as original:
            image = ImageOps.exif_transpose(original).convert('RGB')
            record['original_size'] = list(image.size)
            image.thumbnail((CONFIG['max_edge'], CONFIG['max_edge']))
            record['ocr_size'] = list(image.size)
            with tempfile.TemporaryDirectory(prefix='museum-ocr-') as folder:
                image.save(Path(folder)/'input.png')
                result = subprocess.run([binary, str(Path(folder)/'input.png'), 'stdout', '-l', CONFIG['languages'],
                                         '--psm', str(CONFIG['psm']), 'tsv'], env=env, capture_output=True,
                                        text=True, timeout=120, check=True)
        text, words = parse_tsv(result.stdout)
        fraction = sum(w['confidence'] >= 60 for w in words)/len(words) if words else 0
        record.update(text=text, words=words, high_confidence_fraction=round(fraction,3),
                      mean_confidence=round(sum(w['confidence'] for w in words)/len(words),2) if words else 0,
                      status='text_detected' if sum(c.isalpha() for c in text)>=40 and fraction>=.45 else 'needs_manual_transcription')
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        record.update(status='error', error=str(error))
    save(target, record)
    txt = DATA/'ocr/text'/f"{asset['id']}.txt"
    txt.parent.mkdir(parents=True, exist_ok=True)
    txt.write_text(record['text'], encoding='utf-8')
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, choices=range(1,5), default=2)
    parser.add_argument('--force', action='store_true')
    args = parser.parse_args()
    load = lambda name: json.loads((DATA/'metadata'/f'{name}.json').read_text())
    assets, topics, links = load('assets'), load('topics'), load('topic_assets')
    topic_names = {t['id']:t['title'] for t in topics}
    mappings = defaultdict(list)
    for link in links:mappings[link['asset_id']].append(link['topic_id'])
    curated = json.loads((DATA/'curated/documents.json').read_text())
    covered = {a for d in curated if d.get('review_status')=='verified' for a in d['source_asset_ids']}
    binary, env = engine()
    records = {}
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        tasks = [pool.submit(process,a,binary,env,args.force) for a in assets]
        for i, future in enumerate(as_completed(tasks),1):
            record = future.result()
            records[record['asset_id']] = record
            print(f"[{i}/{len(assets)}] {record['filename']}: {record['status']} ({len(record['text'])} chars)",flush=True)
    drafts, queue = [], []
    for asset in assets:
        record = records[asset['id']]
        tids = sorted(set(mappings[asset['id']]))
        doc_id = 'OCR_'+asset['id']
        queue.append({'asset_id':asset['id'], 'filename':asset['original_filename'], 'topic_ids':tids,
                      'ocr_status':record['status'], 'already_has_verified_document':asset['id'] in covered,
                      'characters':len(record['text']), 'mean_confidence':record.get('mean_confidence',0),
                      'source_path':asset['path'], 'document_id':doc_id})
        if not record['text'].strip() or asset['id'] in covered:continue
        drafts.append({'document_id':doc_id,'topic_id':tids[0] if tids else None,'topic_ids':tids,'exhibit_id':None,
                       'title':(' / '.join(topic_names[t] for t in tids)+' — ' if tids else '')+asset['original_filename'],
                       'title_origin':'catalog_and_filename_not_transcribed_heading',
                       'language':'und','ocr_languages':['vi','en'],'source_asset_ids':[asset['id']],
                       'source_filenames':[asset['original_filename']],'review_status':'needs_review','version':1,
                       'text':record['text'],'ocr_status':record['status'],
                       'review_notes':'Automatic OCR; check text, language, reading order and topic against photo before approval.'})
    save(DATA/'ocr/draft_documents.json',drafts)
    save(DATA/'ocr/review_queue.json',queue)
    report = {'assets_total':len(assets),'topics_total':len(topics),
              'ocr_status_counts':dict(Counter(r['status'] for r in records.values())),
              'existing_verified_documents':sum(d.get('review_status')=='verified' for d in curated),
              'draft_documents':len(drafts),'unassigned_assets':[q['filename'] for q in queue if not q['topic_ids']],
              'topics':[{'topic_id':t['id'],'title':t['title'],
                         'photos':sum(t['id'] in q['topic_ids'] for q in queue),
                         'text_detected':sum(t['id'] in q['topic_ids'] and q['ocr_status']=='text_detected' for q in queue),
                         'manual_or_error':sum(t['id'] in q['topic_ids'] and q['ocr_status']!='text_detected' for q in queue)} for t in topics]}
    save(DATA/'ocr/report.json',report)
    print(json.dumps({k:v for k,v in report.items() if k!='topics'},ensure_ascii=False,indent=2))


if __name__ == '__main__':main()
