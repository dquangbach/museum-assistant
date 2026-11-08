import 'dart:convert';
import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:museum_guide_app/data/museum_api.dart';
import 'package:museum_guide_app/data/museum_catalog.dart';

void main() {
  late HttpServer server;
  late MuseumCatalogApi api;

  setUpAll(() async {
    server = await HttpServer.bind(InternetAddress.loopbackIPv4, 0);
    server.listen((request) async {
      final path = request.uri.path;
      Object response;
      if (path == '/api/v1/groups') {
        response = [
          {'id': 'GROUP01', 'title': 'Lịch sử Đà Nẵng', 'sort_order': 1}
        ];
      } else if (path == '/api/v1/topics') {
        response = {
          'items': [
            {
              'id': 'TOPIC005',
              'group_id': 'GROUP01',
              'title': 'Đà Nẵng thời tiền - sơ sử',
              'summary': 'Mô tả mục',
              'materials_notes': '',
              'source_reference': '',
              'review_status': 'needs_review',
            }
          ],
          'total': 1,
          'limit': 100,
          'offset': 0,
        };
      } else if (path == '/api/v1/topics/TOPIC005') {
        response = {
          'id': 'TOPIC005',
          'group_id': 'GROUP01',
          'title': 'Đà Nẵng thời tiền - sơ sử',
          'summary': 'Mô tả mục',
          'materials_notes': '',
          'source_reference': '',
          'review_status': 'needs_review',
        };
      } else if (path == '/api/v1/topics/TOPIC005/assets') {
        response = {
          'items': [
            {
              'id': 'asset-1',
              'original_filename': 'IMG_8798.JPG',
              'file_url': '/api/v1/assets/asset-1/file',
              'review_status': 'needs_review',
            }
          ],
          'total': 1,
          'limit': 100,
          'offset': 0,
        };
      } else if (path == '/api/v1/qr/resolve' &&
          request.uri.queryParameters['value'] == 'museum://topic/TOPIC005') {
        response = {
          'kind': 'topic',
          'id': 'TOPIC005',
          'detail_url': '/api/v1/topics/TOPIC005',
        };
      } else {
        request.response.statusCode = HttpStatus.notFound;
        await request.response.close();
        return;
      }
      request.response.headers.contentType = ContentType.json;
      request.response.write(jsonEncode(response));
      await request.response.close();
    });
    api = MuseumCatalogApi(baseUrl: 'http://127.0.0.1:${server.port}');
  });

  tearDownAll(() => server.close(force: true));

  test('API chuyển nhóm, mục, ảnh và QR thành dữ liệu Flutter', () async {
    final groups = await api.getGroups();
    final topics = await api.getTopics();
    final topic = await api.getTopic('TOPIC005');
    final assets = await api.getTopicAssets('TOPIC005');
    final qr = await api.resolveQr('museum://topic/TOPIC005');

    expect(groups.single.title, 'Lịch sử Đà Nẵng');
    expect(topics.single.id, 'TOPIC005');
    expect(topic.name, 'Đà Nẵng thời tiền - sơ sử');
    expect(topic.description, 'Mô tả mục');
    expect(api.imageUrl(assets.single).toString(),
        'http://127.0.0.1:${server.port}/api/v1/assets/asset-1/file');
    expect(qr.kind, MuseumQrKind.topic);
    expect(qr.id, 'TOPIC005');
  });
}
