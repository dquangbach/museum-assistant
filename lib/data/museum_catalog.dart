/// Điểm đứng mẫu để thử xác nhận vị trí; backend chưa có checkpoint thực tế.
const List<Map<String, String>> museumCheckpoints = [
  {
    'id': 'CP01',
    'name': 'Cửa vào sảnh chính (Tầng 1)',
    'code': 'museum-demo://checkpoint/CP01',
    'desc': 'Gần quầy bán vé & sơ đồ bảo tàng',
    'icon': '🚪',
  },
  {
    'id': 'CP02',
    'name': 'Lối vào Phòng 1 - Cổ vật',
    'code': 'museum-demo://checkpoint/CP02',
    'desc': 'Trước phòng triển lãm Đông Sơn',
    'icon': '🏛️',
  },
  {
    'id': 'CP03',
    'name': 'Ngã rẽ hành lang trung tâm',
    'code': 'museum-demo://checkpoint/CP03',
    'desc': 'Điểm giao giữa Phòng 1 và Phòng 2',
    'icon': '🧭',
  },
  {
    'id': 'CP04',
    'name': 'Cửa Phòng 2 - Gốm sứ',
    'code': 'museum-demo://checkpoint/CP04',
    'desc': 'Trước khu trưng bày gốm Chu Đậu',
    'icon': '🏺',
  },
];

Map<String, String>? findMuseumCheckpoint(String id) {
  for (final checkpoint in museumCheckpoints) {
    if (checkpoint['id'] == id) return checkpoint;
  }
  return null;
}

enum MuseumQrKind { topic, exhibit, checkpoint }

class MuseumQrResult {
  final MuseumQrKind kind;
  final String id;

  const MuseumQrResult(this.kind, this.id);
}

/// Checkpoint chỉ tồn tại ở máy; QR topic/exhibit phải được backend xác nhận.
MuseumQrResult? resolveMuseumCheckpointQr(String rawValue) {
  final uri = Uri.tryParse(rawValue.trim());
  if (uri == null ||
      uri.scheme != 'museum-demo' ||
      uri.host != 'checkpoint' ||
      uri.pathSegments.length != 1 ||
      uri.hasQuery ||
      uri.hasFragment) {
    return null;
  }
  final id = uri.pathSegments.single.toUpperCase();
  return findMuseumCheckpoint(id) == null
      ? null
      : MuseumQrResult(MuseumQrKind.checkpoint, id);
}
