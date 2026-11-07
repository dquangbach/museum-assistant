/// Dữ liệu demo còn được các màn Flutter hiện tại sử dụng.
/// Danh mục thật gồm các chủ đề TOPIC001...TOPIC038 nằm ở FastAPI/PostgreSQL.
/// Khi nối API, màn danh sách sẽ đọc /api/v1/topics thay cho museumExhibits.
const List<Map<String, String>> museumExhibits = [
  {
    'id': 'EX01',
    'name': 'Trống đồng Đông Sơn',
    'period': 'Khoảng thế kỷ 3 TCN',
    'room': 'Phòng 1 - Cổ vật',
    'cabinet': 'Tủ trung tâm A01',
    'desc':
        'Bảo vật quốc gia thời kỳ văn hóa Đông Sơn. Hoa văn hình sao nhiều cánh, chim Lạc bay và cảnh sinh hoạt lễ hội giã gạo của người Việt cổ được chạm khắc vô cùng tinh xảo.',
    'symbol': '🥁',
  },
  {
    'id': 'EX02',
    'name': 'Tượng Phật Bà Quan Âm',
    'period': 'Thế kỷ 17 · Thời Hậu Lê',
    'room': 'Phòng 1 - Cổ vật',
    'cabinet': 'Bệ điêu khắc B02',
    'desc':
        'Tác phẩm điêu khắc gỗ sơn son thếp vàng đỉnh cao với hình tượng nghìn mắt nghìn tay, thể hiện lòng từ bi phổ độ chúng sinh và triết lý Phật giáo sâu sắc.',
    'symbol': '🪷',
  },
  {
    'id': 'EX03',
    'name': 'Bình gốm hoa lam',
    'period': 'Thế kỷ 15 · Thời Lê Sơ',
    'room': 'Phòng 2 - Gốm sứ',
    'cabinet': 'Tủ trưng bày C05',
    'desc':
        'Hiện vật tiêu biểu của dòng gốm Chu Đậu nổi tiếng thế giới. Kỹ thuật vẽ lam dưới men với các đồ án thiên nga, hoa sen mang đậm bản sắc văn hóa dân gian Việt.',
    'symbol': '🏺',
  },
];

/// Điểm đứng mẫu. Backend hiện chưa có dữ liệu checkpoint thực tế.
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

Map<String, String>? findMuseumExhibit(String id) {
  for (final exhibit in museumExhibits) {
    if (exhibit['id'] == id) return exhibit;
  }
  return null;
}

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

MuseumQrResult? resolveMuseumQr(String rawValue) {
  final uri = Uri.tryParse(rawValue.trim());
  if (uri == null ||
      (uri.scheme != 'museum' && uri.scheme != 'museum-demo') ||
      uri.pathSegments.length != 1 ||
      uri.hasQuery ||
      uri.hasFragment) {
    return null;
  }

  final id = uri.pathSegments.single.toUpperCase();
  // Chỉ kiểm tra cú pháp ở đây; API sẽ xác nhận chủ đề có tồn tại hay không.
  if (uri.host == 'topic' && RegExp(r'^TOPIC[0-9]{3}$').hasMatch(id)) {
    return MuseumQrResult(MuseumQrKind.topic, id);
  }
  // Hai loại bên dưới vẫn phục vụ luồng demo cũ cho tới khi các màn dùng API.
  if (uri.host == 'exhibit' && findMuseumExhibit(id) != null) {
    return MuseumQrResult(MuseumQrKind.exhibit, id);
  }
  if (uri.host == 'checkpoint' && findMuseumCheckpoint(id) != null) {
    return MuseumQrResult(MuseumQrKind.checkpoint, id);
  }
  return null;
}
