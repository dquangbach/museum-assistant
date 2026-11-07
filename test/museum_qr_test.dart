import 'package:flutter_test/flutter_test.dart';
import 'package:museum_guide_app/data/museum_catalog.dart';

void main() {
  test('QR hiện vật mở đúng hiện vật trong danh mục', () {
    final result = resolveMuseumQr('museum-demo://exhibit/EX01');
    expect(result?.kind, MuseumQrKind.exhibit);
    expect(findMuseumExhibit(result!.id)?['name'], 'Trống đồng Đông Sơn');
  });

  test('QR điểm đứng tra đúng checkpoint', () {
    final result = resolveMuseumQr('museum-demo://checkpoint/CP01');
    expect(result?.kind, MuseumQrKind.checkpoint);
    expect(findMuseumCheckpoint(result!.id)?['name'],
        'Cửa vào sảnh chính (Tầng 1)');
  });

  test('QR lạ hoặc ID không có trong danh mục bị từ chối', () {
    expect(resolveMuseumQr('https://example.com'), isNull);
    expect(resolveMuseumQr('museum-demo://exhibit/EX99'), isNull);
    expect(resolveMuseumQr('museum-demo://exhibit/EX01/extra'), isNull);
  });
}
