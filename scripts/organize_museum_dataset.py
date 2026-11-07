#!/usr/bin/env python3
"""Organize original museum photos from a Markdown catalog; no image conversion."""
import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import unicodedata
from urllib.parse import quote
import uuid

IMAGE_SUFFIXES = {'.jpg', '.jpeg', '.png', '.heic', '.webp'}


def digest(path):
    value = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            value.update(chunk)
    return value.hexdigest()


def slug(text):
    text = text.lower().replace('đ', 'd')
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode()
    return re.sub(r'[^a-z0-9]+', '_', text).strip('_')


def referenced_names(source):
    result = []
    for part in source.rstrip('.').split(';'):
        part = part.strip()
        if part.lower().endswith(('.jpg', '.jpeg', '.png', '.heic', '.webp')):
            result.append(part)
            continue
        match = re.fullmatch(r'(\d+)(?:[–-](\d+))?', part)
        if not match:
            raise ValueError(f'Unsupported source reference: {part}')
        start, end = match.groups()
        result.extend(f'IMG_{number}.JPG' for number in range(int(start), int(end or start) + 1))
    return result


def parse_catalog(text):
    groups, topics = [], []
    pattern = r'^## ([IVX]+)\. ([^\n]+)\n(.*?)(?=^## [IVX]+\. |\Z)'
    for order, section in enumerate(re.finditer(pattern, text, re.M | re.S), 1):
        roman, title, body = section.groups()
        group_id = f'GROUP{order:02}'
        directory = f'{order:02}_{slug(title)}'
        groups.append({'id': group_id, 'title': title, 'sort_order': order, 'directory': directory})
        for item in re.finditer(r'^### (\d+)\. ([^\n]+)\n(.*?)(?=^### |\Z)', body, re.M | re.S):
            number, title, content = item.groups()
            source = re.search(r'\*\*Ảnh nguồn:\*\* ([^\n]+)', content)
            materials = re.search(r'\*\*Hiện vật và tư liệu:\*\* ([^\n]+)', content)
            if not source or not materials:
                raise ValueError(f'Incomplete topic {number}')
            topic_id = f'TOPIC{int(number):03}'
            topic_path = f'topics/{directory}/{topic_id}_{slug(title)}'
            topics.append({
                'id': topic_id, 'group_id': group_id, 'catalog_number': int(number),
                'title': title, 'summary': content.split('**Hiện vật và tư liệu:**', 1)[0].strip(),
                'materials_notes': materials.group(1), 'source_reference': source.group(1),
                'review_status': 'needs_review', 'directory': topic_path,
                '_references': referenced_names(source.group(1)),
            })
    if [topic['catalog_number'] for topic in topics] != list(range(1, 39)):
        raise ValueError('Expected exactly 38 consecutively numbered topics')
    return groups, topics


def verify(dataset):
    metadata = dataset / 'metadata'
    manifest = json.loads((metadata / 'source_manifest.json').read_text())
    assets = json.loads((metadata / 'assets.json').read_text())
    topics = json.loads((metadata / 'topics.json').read_text())
    links = json.loads((metadata / 'topic_assets.json').read_text())
    actual = {p.relative_to(dataset).as_posix() for p in dataset.rglob('*') if p.is_file() and p.suffix.lower() in IMAGE_SUFFIXES}
    expected = {row['current_path'] for row in manifest['files']}
    if actual != expected:
        raise ValueError(f'Image inventory mismatch: missing={expected-actual}, unexpected={actual-expected}')
    for row in manifest['files']:
        path = dataset / row['current_path']
        if path.stat().st_size != row['size_bytes'] or digest(path) != row['sha256']:
            raise ValueError(f'Changed photo content: {path}')
    asset_ids = {row['id'] for row in assets}
    topic_ids = {row['id'] for row in topics}
    if len(asset_ids) != len(assets) or len(topic_ids) != len(topics):
        raise ValueError('Duplicate IDs')
    if len({(row['topic_id'], row['asset_id']) for row in links}) != len(links):
        raise ValueError('Duplicate topic-asset relationship')
    for row in links:
        if row['asset_id'] not in asset_ids or row['topic_id'] not in topic_ids:
            raise ValueError('Broken topic-asset relationship')
    for row in assets:
        if not (dataset / row['path']).is_file():
            raise ValueError(f'Missing asset: {row["path"]}')
    print(json.dumps({'verified_images': len(actual), 'verified_topics': len(topics),
                      'verified_relationships': len(links), 'sha256_unchanged': True}, ensure_ascii=False))


def organize(root, apply):
    dataset = root / 'Dataset'
    catalog = root / 'danh_muc_bao_tang.md'
    if (dataset / 'metadata/source_manifest.json').exists():
        verify(dataset)
        print('Dataset already organized; no files moved.')
        return
    if any(p.is_dir() for p in dataset.iterdir()):
        raise ValueError('Expected a flat Dataset; existing subdirectories require manual review')
    text = catalog.read_text(encoding='utf-8')
    groups, topics = parse_catalog(text)
    files = {p.name: p for p in dataset.iterdir() if p.is_file() and p.suffix.lower() in IMAGE_SUFFIXES}
    associations = defaultdict(list)
    gaps = []
    for topic in topics:
        for name in topic['_references']:
            if name in files:
                associations[name].append(topic)
            else:
                gaps.append({'topic_id': topic['id'], 'filename': name, 'reason': 'not_present_in_source_range'})
    assets, links, moves = [], [], []
    timestamp = datetime.now(timezone.utc).isoformat()
    for name, path in sorted(files.items()):
        matches = associations[name]
        if len(matches) == 1:
            destination = f'{matches[0]["directory"]}/{name}'
        elif matches:
            destination = f'shared/{name}'
        else:
            destination = f'unassigned/{name}'
        asset_id = str(uuid.uuid5(uuid.NAMESPACE_URL, f'museum-danang/source-photo/{name}'))
        sha256 = digest(path)
        size = path.stat().st_size
        assets.append({'id': asset_id, 'original_filename': name, 'path': destination,
                       'media_type': 'image/jpeg' if path.suffix.lower() in {'.jpg', '.jpeg'} else None,
                       'size_bytes': size, 'sha256': sha256, 'asset_role': 'unclassified',
                       'review_status': 'needs_review',
                       'classification_status': 'shared' if len(matches) > 1 else 'assigned' if matches else 'unassigned'})
        for topic in matches:
            links.append({'topic_id': topic['id'], 'asset_id': asset_id,
                          'sort_order': topic['_references'].index(name) + 1,
                          'assignment_source': 'danh_muc_bao_tang.md', 'review_status': 'needs_review'})
        moves.append({'asset_id': asset_id, 'original_path': name, 'current_path': destination,
                      'size_bytes': size, 'sha256': sha256})
    unassigned = [a['original_filename'] for a in assets if a['classification_status'] == 'unassigned']
    shared = [{'filename': name, 'topic_ids': [t['id'] for t in matches]}
              for name, matches in associations.items() if len(matches) > 1]
    hash_names = defaultdict(list)
    for asset in assets:
        hash_names[asset['sha256']].append(asset['original_filename'])
    summary = {'actual_image_count': len(assets), 'catalog_stated_image_count': 237,
               'image_count_difference': len(assets) - 237, 'topic_count': len(topics),
               'group_count': len(groups), 'relationship_count': len(links),
               'total_image_bytes': sum(a['size_bytes'] for a in assets),
               'unassigned': unassigned, 'shared': shared, 'range_gaps': gaps,
               'range_gaps_note': 'Catalog ranges may intentionally skip numbers; these are not confirmed lost files.',
               'identical_content_groups': [names for names in hash_names.values() if len(names) > 1]}
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if not apply:
        print('Dry run only. Use --apply to organize photos.')
        return
    for row in moves:
        if (dataset / row['current_path']).exists():
            raise FileExistsError(row['current_path'])
    metadata = dataset / 'metadata'
    metadata.mkdir()
    manifest = {'version': 1, 'created_at': timestamp, 'path_base': 'Dataset/',
                'source_catalog': '../danh_muc_bao_tang.md', 'source_catalog_sha256': digest(catalog), 'files': moves}
    def write_json(name, value):
        (metadata / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    # Save the recovery map before moving any original photo.
    write_json('source_manifest.json', manifest)
    for row in moves:
        destination = dataset / row['current_path']
        destination.parent.mkdir(parents=True, exist_ok=True)
        (dataset / row['original_path']).rename(destination)
    (dataset / 'shared').mkdir(exist_ok=True)
    (dataset / 'unassigned').mkdir(exist_ok=True)
    for topic in topics:
        folder = dataset / topic['directory']
        folder.mkdir(parents=True, exist_ok=True)
        photo_lines = []
        for name in topic['_references']:
            if name in files:
                asset = next(a for a in assets if a['original_filename'] == name)
                import os
                relative = os.path.relpath(dataset / asset['path'], folder)
                photo_lines.append(f'- [{name}]({quote(relative)})')
        notes = '\n\n'.join([f'# {topic["id"]} - {topic["title"]}',
                               '**Trạng thái:** Phân loại sơ bộ theo danh mục; cần đối chiếu nhãn gốc.',
                               topic['summary'], f'**Hiện vật và tư liệu:** {topic["materials_notes"]}',
                               f'**Ảnh nguồn ghi trong danh mục:** {topic["source_reference"]}',
                               '## Ảnh hiện có\n\n' + '\n'.join(photo_lines)])
        (folder / 'README.md').write_text(notes + '\n', encoding='utf-8')
    write_json('groups.json', groups)
    write_json('topics.json', [{k: v for k, v in t.items() if not k.startswith('_')} for t in topics])
    write_json('assets.json', assets)
    write_json('topic_assets.json', links)
    write_json('classification_report.json', summary)
    (metadata / 'catalog_source.md').write_text(text, encoding='utf-8')
    (dataset / 'README.md').write_text('''# Nguồn dữ liệu Bảo tàng Đà Nẵng

Ảnh khảo sát được phân nhóm theo `danh_muc_bao_tang.md`. Tên ảnh và nội dung ảnh gốc được giữ nguyên. Đây là dữ liệu biên tập sơ bộ để chuẩn bị nhập backend; chưa phải nội dung thuyết minh đã được xác minh.

```text
Dataset/
├── topics/                 # 5 nhóm lớn, 38 thư mục chủ đề có README và ảnh gốc
├── shared/                 # Một bản ảnh được nhiều chủ đề tham chiếu
├── unassigned/             # Ảnh có thật nhưng danh mục chưa chỉ định chủ đề
└── metadata/
    ├── groups.json         # Nhóm chủ đề
    ├── topics.json         # Chủ đề, mô tả và nguồn tham chiếu
    ├── assets.json         # Một bản ghi cho mỗi ảnh; đường dẫn, kích thước, SHA-256
    ├── topic_assets.json   # Quan hệ nhiều-nhiều giữa chủ đề và ảnh
    ├── source_manifest.json # Đường dẫn trước/sau để kiểm tra hoặc khôi phục
    ├── classification_report.json # Chênh lệch số ảnh, khoảng số khuyết, ảnh dùng chung
    └── catalog_source.md   # Bản chụp danh mục dùng khi phân loại
```

## Cách dùng cho database

Nhập theo thứ tự `groups.json` → `topics.json` và `assets.json` → `topic_assets.json`. Trường `group_id`, `topic_id`, `asset_id` dùng để liên kết các bản ghi. Các file JSON là mảng bản ghi UTF-8. Đường dẫn `path` và `directory` đều tính từ thư mục `Dataset/`, dùng dấu `/`, không phụ thuộc đường dẫn máy cá nhân. Sau khi upload ảnh lên Storage, backend lưu thêm storage key hoặc URL tương ứng cho mỗi asset ID; không dùng đường dẫn máy cá nhân làm URL công khai.

Mã TOPIC001 đến TOPIC038 là mã chủ đề do dự án cấp theo thứ tự danh mục, chưa phải mã kiểm kê bảo tàng. Một chủ đề có thể chứa nhiều hiện vật. Cần tạo bản ghi `exhibits` và quan hệ `exhibit_assets` sau khi đọc nhãn để xác định từng hiện vật; không tự coi mỗi ảnh hoặc mỗi chủ đề là một hiện vật.

`review_status = needs_review` và `asset_role = unclassified` thể hiện dữ liệu đang chờ đối chiếu. Chưa suy đoán tầng, phòng, tọa độ, tên hiện vật, vai trò ảnh (nhãn/toàn cảnh/hiện vật) hoặc nội dung OCR từ số thứ tự ảnh. Chỉ bổ sung khi có căn cứ từ ảnh hoặc khảo sát.

## Các điểm cần đối chiếu

- Có 236 ảnh thực tế; danh mục ghi 237 ảnh. Chênh lệch chưa xác định nguyên nhân.
- IMG_8991.JPG có trong nguồn nhưng không được liệt kê ở chủ đề nào; nằm trong `unassigned/`.
- IMG_9035.JPG được cả TOPIC030 và TOPIC031 tham chiếu; lưu một lần trong `shared/`, giữ hai quan hệ trong `topic_assets.json`.
- Các dải ảnh trong danh mục có thể khuyết số. `classification_report.json` ghi các tên không hiện diện trong dải để kiểm tra; không khẳng định ảnh bị mất.
- Ảnh có nội dung giống nhau hoàn toàn (nếu có) vẫn được giữ; xem `identical_content_groups` trong báo cáo.

## Kiểm tra và khôi phục

Từ thư mục dự án chạy `python3 scripts/organize_museum_dataset.py --verify` để đối chiếu đủ ảnh, kích thước, SHA-256 và khóa liên kết. Chạy lại `--apply` khi đã sắp xếp chỉ kiểm tra, không di chuyển lần nữa. `source_manifest.json` lưu tên gốc và vị trí mới của từng ảnh; dùng các cặp đường dẫn đó để đưa ảnh về cấu trúc phẳng khi cần. Nếu dừng giữa quá trình di chuyển, mỗi ảnh phải có ở đường dẫn gốc hoặc đường dẫn mới ghi trong manifest; xử lý phần còn lại dựa trên manifest trước khi chạy lại.
''', encoding='utf-8')
    verify(dataset)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--apply', action='store_true')
    mode.add_argument('--verify', action='store_true')
    args = parser.parse_args()
    if args.verify:
        verify(args.root / 'Dataset')
    else:
        organize(args.root, args.apply)


if __name__ == '__main__':
    main()
