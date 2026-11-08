import 'package:flutter_test/flutter_test.dart';
import 'package:museum_guide_app/data/museum_catalog.dart';

void main() {
  test('QR checkpoint demo xác nhận được vị trí', () {
    final result = resolveMuseumCheckpointQr('museum-demo://checkpoint/CP01');
    expect(result?.kind, MuseumQrKind.checkpoint);
    expect(findMuseumCheckpoint(result!.id)?['name'],
        'Cửa vào sảnh chính (Tầng 1)');
  });

  test('QR chủ đề và hiện vật cần backend xác nhận', () {
    expect(resolveMuseumCheckpointQr('museum://topic/TOPIC005'), isNull);
    expect(resolveMuseumCheckpointQr('museum://exhibit/EX01'), isNull);
    expect(resolveMuseumCheckpointQr('museum-demo://checkpoint/CP99'), isNull);
    expect(resolveMuseumCheckpointQr('https://example.com'), isNull);
  });
}
