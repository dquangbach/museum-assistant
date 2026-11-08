import 'package:flutter/material.dart';

import '../data/museum_api.dart';
import '../data/museum_catalog.dart';
import '../models/museum_asset.dart';
import '../models/museum_topic.dart';
import '../state/app_state.dart';
import 'exhibit_detail_screen.dart';
import 'location_picker_screen.dart';
import 'qr_scanner_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key, this.api});

  final MuseumCatalogApi? api;

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  static const _ink = Color(0xFF121212);
  static const _surface = Color(0xFF1A1A1A);
  static const _copper = Color(0xFFEAC0A2);
  static const _muted = Color(0xFF8E8E93);

  late final MuseumCatalogApi _api;
  final Map<String, Future<MuseumAsset?>> _covers = {};
  List<MuseumGroup> _groups = [];
  List<MuseumTopic> _topics = [];
  String? _selectedGroupId;
  String? _error;
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _api = widget.api ?? MuseumCatalogApi();
    _loadCatalog();
  }

  Future<void> _loadCatalog() async {
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final groups = await _api.getGroups();
      final topics = await _api.getTopics();
      if (!mounted) return;
      setState(() {
        _groups = groups;
        _topics = topics;
        _covers.clear();
        _loading = false;
      });
    } catch (error) {
      if (!mounted) return;
      setState(() {
        _error = error.toString();
        _loading = false;
      });
    }
  }

  Future<MuseumAsset?> _coverFor(String topicId) =>
      _covers.putIfAbsent(topicId, () async {
        final assets = await _api.getTopicAssets(topicId);
        return assets.isEmpty ? null : assets.first;
      });

  void _openTopic(MuseumTopic topic) {
    AppStateScope.of(context).selectExhibit(topic.id, topic.title);
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (_) => TopicDetailScreen(topicId: topic.id, api: _api),
      ),
    );
  }

  Future<void> _scanQr() async {
    final result = await Navigator.push<MuseumQrResult>(
      context,
      MaterialPageRoute(builder: (_) => QrScannerScreen(api: _api)),
    );
    if (!mounted || result == null) return;
    if (result.kind == MuseumQrKind.checkpoint) {
      final checkpoint = findMuseumCheckpoint(result.id);
      if (checkpoint == null) return;
      AppStateScope.of(context).updateLocation(checkpoint['name']!, isQr: true);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Đã xác nhận vị trí: ${checkpoint['name']}')),
      );
      return;
    }
    try {
      final topicId = result.kind == MuseumQrKind.topic
          ? result.id
          : await _api.getExhibitTopicId(result.id);
      if (!mounted) return;
      Navigator.push(
        context,
        MaterialPageRoute(
          builder: (_) => TopicDetailScreen(topicId: topicId, api: _api),
        ),
      );
    } catch (error) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Không mở được mục: $error')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final appState = AppStateScope.of(context);
    final visibleTopics = _selectedGroupId == null
        ? _topics
        : _topics.where((topic) => topic.groupId == _selectedGroupId).toList();
    final groupNames = {for (final group in _groups) group.id: group.title};
    final featured = visibleTopics.isEmpty ? null : visibleTopics.first;

    return Scaffold(
      backgroundColor: _ink,
      body: SafeArea(
        child: RefreshIndicator(
          onRefresh: _loadCatalog,
          color: _copper,
          child: ListView(
            padding: const EdgeInsets.fromLTRB(20, 18, 20, 32),
            children: [
              Row(children: [
                const Icon(Icons.account_balance_outlined, color: _copper),
                const SizedBox(width: 10),
                const Text('MUSEO',
                    style: TextStyle(
                        color: Colors.white,
                        fontFamily: 'serif',
                        fontSize: 22,
                        letterSpacing: 2)),
                const Spacer(),
                IconButton(
                  tooltip: 'Tải lại danh mục',
                  onPressed: _loadCatalog,
                  icon: const Icon(Icons.refresh, color: _copper),
                ),
              ]),
              const SizedBox(height: 30),
              const Text('BẢO TÀNG ĐÀ NẴNG',
                  style: TextStyle(
                      color: _copper,
                      fontSize: 10,
                      fontWeight: FontWeight.bold,
                      letterSpacing: 2)),
              const SizedBox(height: 10),
              const Text('Khám phá những\ncâu chuyện di sản.',
                  style: TextStyle(
                      color: Colors.white,
                      fontFamily: 'serif',
                      fontSize: 32,
                      height: 1.12)),
              const SizedBox(height: 12),
              const Text('Chọn một mục trưng bày hoặc quét mã QR tại bảo tàng.',
                  style: TextStyle(color: _muted, fontSize: 13)),
              const SizedBox(height: 24),
              if (_loading)
                const Padding(
                  padding: EdgeInsets.symmetric(vertical: 80),
                  child:
                      Center(child: CircularProgressIndicator(color: _copper)),
                )
              else if (_error != null)
                _errorCard()
              else ...[
                if (featured != null) _featuredCard(featured),
                const SizedBox(height: 16),
                _scanButton(),
                const SizedBox(height: 22),
                _locationCard(appState),
                const SizedBox(height: 28),
                Row(children: [
                  const Expanded(
                    child: Text('Không gian trưng bày',
                        style: TextStyle(
                            color: Colors.white,
                            fontFamily: 'serif',
                            fontSize: 23)),
                  ),
                  Text('${visibleTopics.length} MỤC',
                      style: const TextStyle(color: _muted, fontSize: 10)),
                ]),
                const SizedBox(height: 14),
                SingleChildScrollView(
                  scrollDirection: Axis.horizontal,
                  child: Row(children: [
                    _groupChip('Tất cả', null),
                    for (final group in _groups)
                      _groupChip(group.title, group.id),
                  ]),
                ),
                const SizedBox(height: 16),
                if (visibleTopics.isEmpty)
                  const Padding(
                    padding: EdgeInsets.all(24),
                    child: Text('Chưa có mục trưng bày trong nhóm này.',
                        style: TextStyle(color: _muted)),
                  ),
                for (final topic in visibleTopics)
                  Padding(
                    padding: const EdgeInsets.only(bottom: 12),
                    child: _topicCard(topic, groupNames[topic.groupId]),
                  ),
              ],
            ],
          ),
        ),
      ),
    );
  }

  Widget _errorCard() => Container(
        padding: const EdgeInsets.all(20),
        decoration: BoxDecoration(
          color: _surface,
          borderRadius: BorderRadius.circular(20),
        ),
        child: Column(children: [
          const Icon(Icons.wifi_off, color: _copper, size: 34),
          const SizedBox(height: 12),
          const Text('Không tải được danh mục',
              style: TextStyle(color: Colors.white, fontSize: 17)),
          const SizedBox(height: 8),
          Text(_error!,
              textAlign: TextAlign.center,
              style: const TextStyle(color: _muted, fontSize: 12)),
          const SizedBox(height: 12),
          TextButton(onPressed: _loadCatalog, child: const Text('Thử lại')),
        ]),
      );

  Widget _featuredCard(MuseumTopic topic) => Material(
        color: _surface,
        borderRadius: BorderRadius.circular(24),
        child: InkWell(
          onTap: () => _openTopic(topic),
          borderRadius: BorderRadius.circular(24),
          child: SizedBox(
            height: 300,
            child: ClipRRect(
              borderRadius: BorderRadius.circular(24),
              child: Stack(fit: StackFit.expand, children: [
                FutureBuilder<MuseumAsset?>(
                  future: _coverFor(topic.id),
                  builder: (context, snapshot) {
                    if (!snapshot.hasData) {
                      return const ColoredBox(color: Color(0xFF40332C));
                    }
                    return Image.network(
                      _api.imageUrl(snapshot.data!).toString(),
                      fit: BoxFit.cover,
                      errorBuilder: (_, __, ___) =>
                          const ColoredBox(color: Color(0xFF40332C)),
                    );
                  },
                ),
                const DecoratedBox(
                  decoration: BoxDecoration(
                    gradient: LinearGradient(
                      begin: Alignment.topCenter,
                      end: Alignment.bottomCenter,
                      colors: [Colors.transparent, Color(0xE6000000)],
                    ),
                  ),
                ),
                Positioned(
                  left: 20,
                  right: 20,
                  bottom: 20,
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(topic.id,
                          style: const TextStyle(
                              color: _copper,
                              fontSize: 10,
                              letterSpacing: 1.5)),
                      const SizedBox(height: 7),
                      Text(topic.title,
                          maxLines: 2,
                          overflow: TextOverflow.ellipsis,
                          style: const TextStyle(
                              color: Colors.white,
                              fontFamily: 'serif',
                              fontSize: 28)),
                      const SizedBox(height: 8),
                      const Row(children: [
                        Text('Khám phá mục trưng bày',
                            style: TextStyle(color: _copper, fontSize: 12)),
                        SizedBox(width: 8),
                        Icon(Icons.arrow_forward, color: _copper, size: 16),
                      ]),
                    ],
                  ),
                ),
              ]),
            ),
          ),
        ),
      );

  Widget _scanButton() => SizedBox(
        width: double.infinity,
        child: FilledButton.icon(
          onPressed: _scanQr,
          icon: const Icon(Icons.qr_code_scanner),
          label: const Text('Quét mã QR tại bảo tàng'),
          style: FilledButton.styleFrom(
            backgroundColor: _copper,
            foregroundColor: _ink,
            padding: const EdgeInsets.all(16),
          ),
        ),
      );

  Widget _locationCard(AppState appState) => Container(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
        decoration: BoxDecoration(
          color: _surface,
          borderRadius: BorderRadius.circular(18),
        ),
        child: Row(children: [
          const Icon(Icons.place_outlined, color: _copper),
          const SizedBox(width: 12),
          Expanded(
            child: Text(appState.confirmedLocation ?? 'Chưa xác nhận vị trí',
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
                style: const TextStyle(color: Colors.white)),
          ),
          TextButton(
            onPressed: () => Navigator.push(
              context,
              MaterialPageRoute(
                builder: (_) => LocationPickerScreen(api: _api),
              ),
            ),
            child: const Text('Chọn điểm'),
          ),
        ]),
      );

  Widget _groupChip(String label, String? id) {
    final selected = _selectedGroupId == id;
    return Padding(
      padding: const EdgeInsets.only(right: 8),
      child: ChoiceChip(
        label: Text(label),
        selected: selected,
        onSelected: (_) => setState(() => _selectedGroupId = id),
        showCheckmark: false,
        backgroundColor: _surface,
        selectedColor: _copper,
        labelStyle: TextStyle(color: selected ? _ink : _muted),
      ),
    );
  }

  Widget _topicCard(MuseumTopic topic, String? groupName) => Material(
        color: _surface,
        borderRadius: BorderRadius.circular(18),
        child: InkWell(
          onTap: () => _openTopic(topic),
          borderRadius: BorderRadius.circular(18),
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Row(children: [
              Container(
                width: 58,
                height: 72,
                decoration: BoxDecoration(
                  color: const Color(0xFF332A25),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: const Icon(Icons.museum_outlined, color: _copper),
              ),
              const SizedBox(width: 14),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(groupName ?? topic.groupId,
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                        style: const TextStyle(color: _copper, fontSize: 10)),
                    const SizedBox(height: 5),
                    Text(topic.title,
                        maxLines: 2,
                        overflow: TextOverflow.ellipsis,
                        style: const TextStyle(
                            color: Colors.white,
                            fontFamily: 'serif',
                            fontSize: 17)),
                    const SizedBox(height: 5),
                    Text(topic.id,
                        style: const TextStyle(color: _muted, fontSize: 10)),
                  ],
                ),
              ),
              const Icon(Icons.chevron_right, color: _muted),
            ]),
          ),
        ),
      );
}
