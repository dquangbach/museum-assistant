import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:museum_guide_app/data/museum_api.dart';
import 'package:museum_guide_app/models/museum_asset.dart';
import 'package:museum_guide_app/models/museum_topic.dart';
import 'package:museum_guide_app/screens/home_screen.dart';
import 'package:museum_guide_app/state/app_state.dart';

class FakeCatalogApi extends MuseumCatalogApi {
  @override
  Future<List<MuseumGroup>> getGroups() async =>
      [const MuseumGroup(id: 'GROUP01', title: 'Lịch sử Đà Nẵng')];

  @override
  Future<List<MuseumTopic>> getTopics({String? groupId}) async => [
        const MuseumTopic(
          id: 'TOPIC005',
          groupId: 'GROUP01',
          title: 'Đà Nẵng thời tiền - sơ sử',
          summary: 'Giới thiệu chủ đề.',
          materialsNotes: '',
          sourceReference: '',
          reviewStatus: 'needs_review',
        ),
      ];

  @override
  Future<List<MuseumAsset>> getTopicAssets(String id) async => [];
}

void main() {
  testWidgets('Trang chủ hiển thị mục từ API thay cho hiện vật demo',
      (tester) async {
    final appState = AppState();
    addTearDown(appState.dispose);
    await tester.pumpWidget(
      AppStateScope(
        notifier: appState,
        child: MaterialApp(home: HomeScreen(api: FakeCatalogApi())),
      ),
    );
    await tester.pumpAndSettle();
    expect(find.text('Đà Nẵng thời tiền - sơ sử'), findsWidgets);
    await tester.drag(find.byType(ListView), const Offset(0, -430));
    await tester.pumpAndSettle();
    expect(find.text('Lịch sử Đà Nẵng'), findsWidgets);
    expect(find.text('Trống đồng Đông Sơn'), findsNothing);
  });
}
