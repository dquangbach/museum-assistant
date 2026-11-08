import 'package:flutter/material.dart';

import '../data/museum_api.dart';
import '../models/museum_asset.dart';
import '../models/museum_topic.dart';

/// Chi tiết một mục trưng bày, không phải một hiện vật đơn lẻ.
class TopicDetailScreen extends StatefulWidget {
  const TopicDetailScreen({super.key, required this.topicId, this.api});

  final String topicId;
  final MuseumCatalogApi? api;

  @override
  State<TopicDetailScreen> createState() => _TopicDetailScreenState();
}

class _TopicDetailScreenState extends State<TopicDetailScreen> {
  static const _ink = Color(0xFF121212);
  static const _surface = Color(0xFF1A1A1A);
  static const _copper = Color(0xFFEAC0A2);
  static const _muted = Color(0xFF8E8E93);

  late final MuseumCatalogApi _api;
  MuseumTopic? _topic;
  List<MuseumAsset> _assets = [];
  String? _error;
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _api = widget.api ?? MuseumCatalogApi();
    _load();
  }

  Future<void> _load() async {
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final topic = await _api.getTopic(widget.topicId);
      final assets = await _api.getTopicAssets(widget.topicId);
      if (!mounted) return;
      setState(() {
        _topic = topic;
        _assets = assets;
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

  void _openImage(MuseumAsset asset) {
    Navigator.push(
      context,
      MaterialPageRoute<void>(
        builder: (_) => Scaffold(
          backgroundColor: Colors.black,
          appBar: AppBar(
            backgroundColor: Colors.black,
            title: Text(asset.originalFilename),
          ),
          body: InteractiveViewer(
            child: Center(
              child: Image.network(
                _api.imageUrl(asset).toString(),
                errorBuilder: (_, __, ___) => const Text(
                  'Không tải được ảnh.',
                  style: TextStyle(color: Colors.white),
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: _ink,
      appBar: AppBar(title: const Text('Mục trưng bày')),
      body: _loading
          ? const Center(child: CircularProgressIndicator(color: _copper))
          : _error != null
              ? Center(
                  child: Padding(
                    padding: const EdgeInsets.all(24),
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        const Icon(Icons.wifi_off, color: _copper, size: 36),
                        const SizedBox(height: 12),
                        Text(_error!,
                            textAlign: TextAlign.center,
                            style: const TextStyle(color: _muted)),
                        TextButton(
                            onPressed: _load, child: const Text('Thử lại')),
                      ],
                    ),
                  ),
                )
              : RefreshIndicator(
                  onRefresh: _load,
                  color: _copper,
                  child: ListView(
                    padding: const EdgeInsets.fromLTRB(20, 10, 20, 32),
                    children: [
                      _hero(),
                      const SizedBox(height: 24),
                      Text(_topic!.id,
                          style: const TextStyle(
                              color: _copper,
                              letterSpacing: 1.6,
                              fontSize: 11)),
                      const SizedBox(height: 8),
                      Text(_topic!.title,
                          style: const TextStyle(
                              color: Colors.white,
                              fontFamily: 'serif',
                              fontSize: 29,
                              height: 1.15)),
                      const SizedBox(height: 18),
                      if (_topic!.reviewStatus != 'verified')
                        const Padding(
                          padding: EdgeInsets.only(bottom: 16),
                          child: Text(
                              'Thông tin đang được đối chiếu với nguồn.',
                              style: TextStyle(color: _muted, fontSize: 12)),
                        ),
                      _section('Giới thiệu', _topic!.summary),
                      if (_topic!.materialsNotes.trim().isNotEmpty)
                        _section('Ghi chú tư liệu', _topic!.materialsNotes),
                      if (_topic!.sourceReference.trim().isNotEmpty)
                        _section('Nguồn', _topic!.sourceReference),
                      const SizedBox(height: 8),
                      Row(children: [
                        const Expanded(
                          child: Text('Ảnh minh họa',
                              style: TextStyle(
                                  color: Colors.white,
                                  fontFamily: 'serif',
                                  fontSize: 22)),
                        ),
                        Text('${_assets.length} ẢNH',
                            style:
                                const TextStyle(color: _muted, fontSize: 10)),
                      ]),
                      const SizedBox(height: 12),
                      if (_assets.isEmpty)
                        const Text('Mục này chưa có ảnh.',
                            style: TextStyle(color: _muted))
                      else
                        LayoutBuilder(
                          builder: (context, constraints) {
                            final columns = constraints.maxWidth >= 600 ? 3 : 2;
                            final width =
                                (constraints.maxWidth - (columns - 1) * 10) /
                                    columns;
                            return Wrap(
                              spacing: 10,
                              runSpacing: 10,
                              children: [
                                for (final asset in _assets)
                                  SizedBox(
                                    width: width,
                                    child: _imageTile(asset),
                                  ),
                              ],
                            );
                          },
                        ),
                    ],
                  ),
                ),
    );
  }

  Widget _hero() => ClipRRect(
        borderRadius: BorderRadius.circular(24),
        child: SizedBox(
          height: 250,
          child: _assets.isEmpty
              ? const ColoredBox(
                  color: _surface,
                  child: Center(
                    child:
                        Icon(Icons.museum_outlined, color: _copper, size: 54),
                  ),
                )
              : Image.network(
                  _api.imageUrl(_assets.first).toString(),
                  fit: BoxFit.cover,
                  errorBuilder: (_, __, ___) => const ColoredBox(
                    color: _surface,
                    child: Center(
                      child: Icon(Icons.broken_image_outlined, color: _copper),
                    ),
                  ),
                ),
        ),
      );

  Widget _section(String title, String text) => Padding(
        padding: const EdgeInsets.only(bottom: 22),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(title,
                style: const TextStyle(
                    color: Colors.white,
                    fontSize: 18,
                    fontWeight: FontWeight.w600)),
            const SizedBox(height: 8),
            Text(text.trim().isEmpty ? 'Chưa có mô tả.' : text,
                style:
                    const TextStyle(color: _muted, fontSize: 14, height: 1.55)),
          ],
        ),
      );

  Widget _imageTile(MuseumAsset asset) => Material(
        color: _surface,
        borderRadius: BorderRadius.circular(14),
        child: InkWell(
          onTap: () => _openImage(asset),
          borderRadius: BorderRadius.circular(14),
          child: ClipRRect(
            borderRadius: BorderRadius.circular(14),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                AspectRatio(
                  aspectRatio: 1,
                  child: Image.network(
                    _api.imageUrl(asset).toString(),
                    fit: BoxFit.cover,
                    errorBuilder: (_, __, ___) => const Center(
                      child: Icon(Icons.broken_image_outlined, color: _muted),
                    ),
                  ),
                ),
                Padding(
                  padding: const EdgeInsets.all(9),
                  child: Text(asset.originalFilename,
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      style: const TextStyle(color: _muted, fontSize: 10)),
                ),
              ],
            ),
          ),
        ),
      );
}
