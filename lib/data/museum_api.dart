import 'dart:async';
import 'dart:convert';
import 'dart:io';

import '../models/museum_asset.dart';
import '../models/museum_topic.dart';
import 'museum_catalog.dart';

/// Địa chỉ máy chạy FastAPI. iPhone thật cần IP LAN, truyền bằng --dart-define.
const museumApiBaseUrl = String.fromEnvironment(
  'API_BASE_URL',
  defaultValue: 'http://localhost:8002',
);

class MuseumGroup {
  final String id;
  final String title;

  const MuseumGroup({required this.id, required this.title});

  factory MuseumGroup.fromJson(Map<String, dynamic> json) => MuseumGroup(
        id: json['id'] as String,
        title: json['title'] as String,
      );
}

class MuseumApiException implements Exception {
  final String message;
  const MuseumApiException(this.message);

  @override
  String toString() => message;
}

/// Nguồn danh mục thật. API trả tối đa 100 mục mỗi trang.
class MuseumCatalogApi {
  final Uri baseUri;

  MuseumCatalogApi({String baseUrl = museumApiBaseUrl})
      : baseUri = Uri.parse(baseUrl.endsWith('/') ? baseUrl : '$baseUrl/');

  Uri _url(String path, [Map<String, String>? query]) =>
      baseUri.resolve('api/v1/$path').replace(queryParameters: query);

  Future<Object?> _getJson(Uri url) async {
    final client = HttpClient()..connectionTimeout = const Duration(seconds: 8);
    try {
      final request =
          await client.getUrl(url).timeout(const Duration(seconds: 8));
      final response =
          await request.close().timeout(const Duration(seconds: 15));
      final body = await utf8.decoder.bind(response).join();
      if (response.statusCode != HttpStatus.ok) {
        throw MuseumApiException('API trả mã ${response.statusCode}: $url');
      }
      final decoded = jsonDecode(body);
      return decoded;
    } on SocketException {
      throw MuseumApiException(
          'Không kết nối được backend tại ${baseUri.origin}.');
    } on HandshakeException {
      throw const MuseumApiException('Không thiết lập được kết nối HTTPS.');
    } on TimeoutException {
      throw const MuseumApiException('Backend phản hồi quá lâu.');
    } on FormatException {
      throw const MuseumApiException('Dữ liệu API không phải JSON hợp lệ.');
    } finally {
      client.close(force: true);
    }
  }

  Future<Map<String, dynamic>> _get(Uri url) async {
    final data = await _getJson(url);
    if (data is! Map<String, dynamic>) {
      throw const MuseumApiException('Dữ liệu API không đúng định dạng.');
    }
    return data;
  }

  Future<List<MuseumGroup>> getGroups() async {
    final data = await _getJson(_url('groups'));
    if (data is! List) {
      throw const MuseumApiException('Danh sách nhóm không đúng định dạng.');
    }
    return data
        .map((item) => MuseumGroup.fromJson(item as Map<String, dynamic>))
        .toList();
  }

  Future<List<MuseumTopic>> getTopics({String? groupId}) async {
    final topics = <MuseumTopic>[];
    const pageSize = 100;
    var offset = 0;
    while (true) {
      final query = {'limit': '$pageSize', 'offset': '$offset'};
      if (groupId != null) query['group_id'] = groupId;
      final page = await _get(_url('topics', query));
      final items = page['items'] as List<dynamic>;
      topics.addAll(items
          .map((item) => MuseumTopic.fromJson(item as Map<String, dynamic>)));
      offset += items.length;
      if (items.isEmpty || offset >= (page['total'] as int)) return topics;
    }
  }

  Future<MuseumTopic> getTopic(String id) async => MuseumTopic.fromJson(
      await _get(_url('topics/${Uri.encodeComponent(id)}')));

  Future<List<MuseumAsset>> getTopicAssets(String id) async {
    final assets = <MuseumAsset>[];
    const pageSize = 100;
    var offset = 0;
    while (true) {
      final page = await _get(_url(
        'topics/${Uri.encodeComponent(id)}/assets',
        {'limit': '$pageSize', 'offset': '$offset'},
      ));
      final items = page['items'] as List<dynamic>;
      assets.addAll(items
          .map((item) => MuseumAsset.fromJson(item as Map<String, dynamic>)));
      offset += items.length;
      if (items.isEmpty || offset >= (page['total'] as int)) return assets;
    }
  }

  Future<String> getExhibitTopicId(String id) async {
    final data = await _get(_url('exhibits/${Uri.encodeComponent(id)}'));
    return data['topic_id'] as String;
  }

  /// URL đầy đủ cho Image.network; file_url từ API là đường dẫn từ gốc server.
  Uri imageUrl(MuseumAsset asset) => baseUri.resolve(asset.fileUrl);

  Future<MuseumQrResult> resolveQr(String value) async {
    final data = await _get(_url('qr/resolve', {'value': value}));
    final kind = switch (data['kind']) {
      'topic' => MuseumQrKind.topic,
      'exhibit' => MuseumQrKind.exhibit,
      _ => throw const MuseumApiException('Loại QR không được hỗ trợ.'),
    };
    return MuseumQrResult(kind, data['id'] as String);
  }
}
