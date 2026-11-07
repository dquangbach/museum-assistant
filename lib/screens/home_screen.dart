import 'package:flutter/material.dart';
import '../data/museum_catalog.dart';
import '../state/app_state.dart';
import 'exhibit_detail_screen.dart';
import 'location_picker_screen.dart';
import 'navigation_screen.dart';
import 'qr_scanner_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  static const _ink = Color(0xFF121212);
  static const _surface = Color(0xFF1A1A1A);
  static const _line = Color(0xFF2A2A2A);
  static const _copper = Color(0xFFEAC0A2);
  static const _muted = Color(0xFF8E8E93);

  String _selectedRoom = 'Tất cả';
  bool _isPlayingAudio = false;
  String _narrationMode = 'Thuyết minh chuyên sâu';

  final List<Map<String, String>> _exhibits = museumExhibits;

  void _openLocationPicker(BuildContext context, {Widget? nextScreen}) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (_) => LocationPickerScreen(
          nextScreenAfterSelection: nextScreen,
        ),
      ),
    );
  }

  Future<void> _scanQr() async {
    final result = await Navigator.push<MuseumQrResult>(
      context,
      MaterialPageRoute(builder: (_) => const QrScannerScreen()),
    );
    if (!mounted || result == null) return;

    final appState = AppStateScope.of(context);
    if (result.kind == MuseumQrKind.exhibit) {
      final exhibit = findMuseumExhibit(result.id);
      if (exhibit != null) _openExhibit(context, appState, exhibit);
      return;
    }

    final checkpoint = findMuseumCheckpoint(result.id);
    if (checkpoint == null) return;
    appState.updateLocation(checkpoint['name']!, isQr: true);
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text('Đã xác nhận vị trí: ${checkpoint['name']}')),
    );
  }

  void _openExhibit(
      BuildContext context, AppState appState, Map<String, String> item) {
    appState.selectExhibit(item['id']!, item['name']!);
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (_) => ExhibitDetailScreen(
          exhibitId: item['id']!,
          exhibitName: item['name']!,
          period: item['period']!,
          room: item['room']!,
          cabinet: item['cabinet']!,
          desc: item['desc']!,
          symbol: item['symbol']!,
        ),
      ),
    );
  }

  void _startNavigation(
      BuildContext context, AppState appState, Map<String, String> item) {
    appState.selectExhibit(item['id']!, item['name']!);
    final destination = NavigationScreen(
      destinationName: item['name']!,
      cabinet: item['cabinet']!,
    );

    if (appState.confirmedLocation == null) {
      _openLocationPicker(context, nextScreen: destination);
      return;
    }

    Navigator.push(context, MaterialPageRoute(builder: (_) => destination));
  }

  @override
  Widget build(BuildContext context) {
    final appState = AppStateScope.of(context);
    final filteredExhibits = _selectedRoom == 'Tất cả'
        ? _exhibits
        : _exhibits.where((item) => item['room'] == _selectedRoom).toList();

    return Scaffold(
      backgroundColor: _ink,
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.fromLTRB(20, 14, 20, 28),
          children: [
            _buildTopBar(context, appState),
            const SizedBox(height: 30),
            const Text(
              'BẢO TÀNG LỊCH SỬ',
              style: TextStyle(
                color: _copper,
                fontSize: 10,
                fontWeight: FontWeight.w700,
                letterSpacing: 2.1,
              ),
            ),
            const SizedBox(height: 10),
            const Text(
              'Mỗi hiện vật\nẩn giấu một câu chuyện.',
              style: TextStyle(
                color: Colors.white,
                fontFamily: 'serif',
                fontSize: 32,
                height: 1.12,
                fontWeight: FontWeight.w500,
                letterSpacing: -0.5,
              ),
            ),
            const SizedBox(height: 10),
            const Text(
              'Chạm vào di sản Việt Nam qua những câu chuyện được kể ngay tại nơi lưu giữ.',
              style: TextStyle(color: _muted, fontSize: 13, height: 1.5),
            ),
            const SizedBox(height: 22),
            _buildFeaturedExhibit(context, appState),
            const SizedBox(height: 14),
            _buildScanButton(),
            const SizedBox(height: 28),
            _buildVisitStatus(context, appState),
            const SizedBox(height: 22),
            _buildNarrationCard(),
            const SizedBox(height: 30),
            _buildCollectionHeader(),
            const SizedBox(height: 14),
            _buildRoomFilters(),
            const SizedBox(height: 14),
            ...filteredExhibits.map(
              (item) => Padding(
                padding: const EdgeInsets.only(bottom: 12),
                child: _buildExhibitCard(context, appState, item),
              ),
            ),
            const SizedBox(height: 8),
            const Center(
              child: Text(
                'ĐI CHẬM LẠI. NHÌN GẦN HƠN.',
                style: TextStyle(
                  color: Color(0xFF686868),
                  fontSize: 9,
                  letterSpacing: 2,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ),
          ],
        ),
      ),
      bottomNavigationBar: _buildAudioPlayer(),
    );
  }

  Widget _buildTopBar(BuildContext context, AppState appState) {
    return Row(
      children: [
        Container(
          width: 38,
          height: 38,
          decoration: BoxDecoration(
            color: _copper,
            borderRadius: BorderRadius.circular(12),
          ),
          child:
              const Icon(Icons.account_balance_outlined, color: _ink, size: 21),
        ),
        const SizedBox(width: 10),
        const Text(
          'MUSEO',
          style: TextStyle(
            color: Colors.white,
            fontFamily: 'serif',
            fontSize: 20,
            letterSpacing: 2.4,
            fontWeight: FontWeight.w600,
          ),
        ),
        const Spacer(),
        Material(
          color: _surface,
          borderRadius: BorderRadius.circular(24),
          child: InkWell(
            borderRadius: BorderRadius.circular(24),
            onTap: () => _openLocationPicker(context),
            child: Container(
              constraints: const BoxConstraints(maxWidth: 172),
              padding: const EdgeInsets.symmetric(horizontal: 11, vertical: 9),
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(24),
                border: Border.all(color: _line),
              ),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  const Icon(Icons.location_on_outlined,
                      color: _copper, size: 16),
                  const SizedBox(width: 6),
                  Flexible(
                    child: Text(
                      appState.confirmedLocation ?? 'Chọn điểm đứng',
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      style: const TextStyle(color: Colors.white, fontSize: 11),
                    ),
                  ),
                  const SizedBox(width: 3),
                  const Icon(Icons.expand_more, color: _muted, size: 15),
                ],
              ),
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildFeaturedExhibit(BuildContext context, AppState appState) {
    final featured = _exhibits.first;
    return ClipRRect(
      borderRadius: BorderRadius.circular(24),
      child: SizedBox(
        height: 332,
        child: Stack(
          fit: StackFit.expand,
          children: [
            Image.asset('assets/images/dong-son-drum.png', fit: BoxFit.cover),
            const DecoratedBox(
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  begin: Alignment.topCenter,
                  end: Alignment.bottomCenter,
                  colors: [
                    Color(0x52000000),
                    Color(0x00000000),
                    Color(0xB8000000),
                    Color(0xF2000000),
                  ],
                  stops: [0, 0.36, 0.69, 1],
                ),
              ),
            ),
            Positioned(
              top: 14,
              left: 14,
              child: _tag('BẢO VẬT QUỐC GIA'),
            ),
            Positioned(
              top: 12,
              right: 12,
              child: Container(
                width: 36,
                height: 36,
                decoration: BoxDecoration(
                  color: Colors.black.withAlpha(110),
                  shape: BoxShape.circle,
                  border: Border.all(color: Colors.white.withAlpha(60)),
                ),
                child: const Icon(Icons.bookmark_border,
                    color: Colors.white, size: 18),
              ),
            ),
            Positioned(
              left: 20,
              right: 20,
              bottom: 18,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'VĂN HÓA ĐÔNG SƠN  ·  THẾ KỶ 3 TCN',
                    style: TextStyle(
                      color: _copper,
                      fontSize: 9,
                      fontWeight: FontWeight.w700,
                      letterSpacing: 1.4,
                    ),
                  ),
                  const SizedBox(height: 6),
                  const Text(
                    'Trống đồng\nĐông Sơn',
                    style: TextStyle(
                      color: Colors.white,
                      fontFamily: 'serif',
                      fontSize: 30,
                      height: 1.04,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                  const SizedBox(height: 13),
                  Row(
                    children: [
                      Expanded(
                        child: TextButton.icon(
                          style: TextButton.styleFrom(
                            foregroundColor: Colors.white,
                            padding: const EdgeInsets.symmetric(horizontal: 0),
                            alignment: Alignment.centerLeft,
                          ),
                          onPressed: () =>
                              _openExhibit(context, appState, featured),
                          icon: const Icon(Icons.arrow_forward,
                              size: 16, color: _copper),
                          label: const Text(
                            'Khám phá hiện vật',
                            style: TextStyle(
                                fontSize: 12, fontWeight: FontWeight.w600),
                          ),
                        ),
                      ),
                      const Icon(Icons.volume_up_outlined,
                          color: Colors.white70, size: 17),
                      const SizedBox(width: 5),
                      const Text('3 phút',
                          style:
                              TextStyle(color: Colors.white70, fontSize: 11)),
                    ],
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _tag(String label) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 7),
      decoration: BoxDecoration(
        color: Colors.black.withAlpha(130),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: Colors.white.withAlpha(50)),
      ),
      child: Text(
        label,
        style: const TextStyle(
          color: Colors.white,
          fontSize: 9,
          letterSpacing: 1,
          fontWeight: FontWeight.w700,
        ),
      ),
    );
  }

  Widget _buildScanButton() {
    return Material(
      color: _copper,
      borderRadius: BorderRadius.circular(16),
      child: InkWell(
        borderRadius: BorderRadius.circular(16),
        onTap: _scanQr,
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
          child: Row(
            children: [
              const Icon(Icons.qr_code_scanner, color: _ink, size: 20),
              const SizedBox(width: 11),
              const Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Quét mã tại bảo tàng',
                      style: TextStyle(
                          color: _ink,
                          fontSize: 13,
                          fontWeight: FontWeight.w700),
                    ),
                    SizedBox(height: 2),
                    Text(
                      'Xem hiện vật hoặc xác định vị trí đứng',
                      style: TextStyle(color: Color(0xFF4F4036), fontSize: 10),
                    ),
                  ],
                ),
              ),
              const Icon(Icons.arrow_forward, color: _ink, size: 18),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildVisitStatus(BuildContext context, AppState appState) {
    final location = appState.confirmedLocation;
    return Container(
      padding: const EdgeInsets.fromLTRB(15, 13, 12, 13),
      decoration: BoxDecoration(
        color: _surface,
        borderRadius: BorderRadius.circular(18),
        border: Border.all(color: _line),
      ),
      child: Row(
        children: [
          Container(
            width: 38,
            height: 38,
            decoration: BoxDecoration(
                color: _copper.withAlpha(24), shape: BoxShape.circle),
            child: const Icon(Icons.route_outlined, color: _copper, size: 19),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'ĐIỂM XUẤT PHÁT',
                  style: TextStyle(
                      color: _muted,
                      fontSize: 9,
                      letterSpacing: 1.2,
                      fontWeight: FontWeight.w700),
                ),
                const SizedBox(height: 3),
                Text(
                  location ?? 'Chưa xác định vị trí',
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                  style: const TextStyle(
                      color: Colors.white,
                      fontSize: 12,
                      fontWeight: FontWeight.w600),
                ),
              ],
            ),
          ),
          TextButton(
            onPressed: () => _openLocationPicker(context),
            style: TextButton.styleFrom(
                foregroundColor: _copper, visualDensity: VisualDensity.compact),
            child: Text(location == null ? 'Chọn' : 'Đổi',
                style: const TextStyle(fontSize: 11)),
          ),
        ],
      ),
    );
  }

  Widget _buildNarrationCard() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 15, vertical: 13),
      decoration: BoxDecoration(
        color: _surface,
        borderRadius: BorderRadius.circular(18),
        border: Border.all(color: _line),
      ),
      child: Row(
        children: [
          Container(
            width: 38,
            height: 38,
            decoration: BoxDecoration(
                color: _copper.withAlpha(24), shape: BoxShape.circle),
            child: const Icon(Icons.graphic_eq, color: _copper, size: 19),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'CÁCH THƯỞNG THỨC',
                  style: TextStyle(
                      color: _muted,
                      fontSize: 9,
                      letterSpacing: 1.2,
                      fontWeight: FontWeight.w700),
                ),
                const SizedBox(height: 3),
                Text(
                  _narrationMode,
                  style: const TextStyle(
                      color: Colors.white,
                      fontSize: 12,
                      fontWeight: FontWeight.w600),
                ),
              ],
            ),
          ),
          TextButton(
            onPressed: () {
              setState(() {
                _narrationMode = _narrationMode == 'Thuyết minh chuyên sâu'
                    ? 'Tóm lược · 2–3 phút'
                    : 'Thuyết minh chuyên sâu';
              });
            },
            style: TextButton.styleFrom(
                foregroundColor: _copper, visualDensity: VisualDensity.compact),
            child: const Text('Đổi', style: TextStyle(fontSize: 11)),
          ),
        ],
      ),
    );
  }

  Widget _buildCollectionHeader() {
    return const Row(
      crossAxisAlignment: CrossAxisAlignment.end,
      children: [
        Expanded(
          child: Text(
            'Không gian trưng bày',
            style: TextStyle(
              color: Colors.white,
              fontFamily: 'serif',
              fontSize: 23,
              fontWeight: FontWeight.w500,
            ),
          ),
        ),
        Text('03 HIỆN VẬT',
            style: TextStyle(color: _muted, fontSize: 9, letterSpacing: 1.2)),
      ],
    );
  }

  Widget _buildRoomFilters() {
    const filters = [
      ('Tất cả', 'Tất cả'),
      ('Phòng 1 - Cổ vật', 'Cổ vật'),
      ('Phòng 2 - Gốm sứ', 'Gốm sứ'),
    ];
    return SingleChildScrollView(
      scrollDirection: Axis.horizontal,
      child: Row(
        children: filters.map((filter) {
          final isSelected = _selectedRoom == filter.$1;
          return Padding(
            padding: const EdgeInsets.only(right: 8),
            child: ChoiceChip(
              label: Text(filter.$2),
              selected: isSelected,
              onSelected: (_) => setState(() => _selectedRoom = filter.$1),
              showCheckmark: false,
              backgroundColor: _surface,
              selectedColor: _copper,
              side: BorderSide(color: isSelected ? _copper : _line),
              labelStyle: TextStyle(
                color: isSelected ? _ink : _muted,
                fontSize: 11,
                fontWeight: FontWeight.w600,
              ),
              shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(20)),
              padding: const EdgeInsets.symmetric(horizontal: 7, vertical: 2),
            ),
          );
        }).toList(),
      ),
    );
  }

  Widget _buildExhibitCard(
      BuildContext context, AppState appState, Map<String, String> item) {
    return Material(
      color: _surface,
      borderRadius: BorderRadius.circular(19),
      child: InkWell(
        onTap: () => _openExhibit(context, appState, item),
        borderRadius: BorderRadius.circular(19),
        child: Container(
          padding: const EdgeInsets.all(11),
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(19),
            border: Border.all(color: _line),
          ),
          child: Row(
            children: [
              _buildArtworkThumbnail(item),
              const SizedBox(width: 13),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      item['room']!.toUpperCase(),
                      style: const TextStyle(
                          color: _copper,
                          fontSize: 8,
                          letterSpacing: 1,
                          fontWeight: FontWeight.w700),
                    ),
                    const SizedBox(height: 5),
                    Text(
                      item['name']!,
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                      style: const TextStyle(
                        color: Colors.white,
                        fontFamily: 'serif',
                        fontSize: 17,
                        height: 1.1,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                    const SizedBox(height: 5),
                    Text(item['period']!,
                        style: const TextStyle(color: _muted, fontSize: 10)),
                    const SizedBox(height: 9),
                    GestureDetector(
                      onTap: () => _startNavigation(context, appState, item),
                      child: const Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Icon(Icons.near_me_outlined,
                              size: 13, color: _copper),
                          SizedBox(width: 4),
                          Text('Chỉ đường',
                              style: TextStyle(
                                  color: _copper,
                                  fontSize: 10,
                                  fontWeight: FontWeight.w600)),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(width: 4),
              const Icon(Icons.arrow_forward_ios,
                  color: Color(0xFF77716D), size: 13),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildArtworkThumbnail(Map<String, String> item) {
    if (item['id'] == 'EX01') {
      return ClipRRect(
        borderRadius: BorderRadius.circular(13),
        child: Image.asset(
          'assets/images/dong-son-drum.png',
          width: 76,
          height: 98,
          fit: BoxFit.cover,
          alignment: const Alignment(0, 0.46),
        ),
      );
    }

    final isStatue = item['id'] == 'EX02';
    return Container(
      width: 76,
      height: 98,
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(13),
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: isStatue
              ? const [Color(0xFF54453B), Color(0xFF241F1B)]
              : const [Color(0xFF3D4844), Color(0xFF1D2422)],
        ),
        border: Border.all(color: Colors.white.withAlpha(14)),
      ),
      child: Icon(
        isStatue
            ? Icons.self_improvement_outlined
            : Icons.local_florist_outlined,
        size: 32,
        color: _copper,
      ),
    );
  }

  Widget _buildAudioPlayer() {
    return SafeArea(
      top: false,
      child: Container(
        padding: const EdgeInsets.fromLTRB(20, 10, 20, 10),
        decoration: const BoxDecoration(
          color: Color(0xFF151515),
          border: Border(top: BorderSide(color: _line)),
        ),
        child: Container(
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 9),
          decoration: BoxDecoration(
            color: _surface,
            borderRadius: BorderRadius.circular(17),
            border: Border.all(color: _line),
          ),
          child: Row(
            children: [
              IconButton.filled(
                onPressed: () =>
                    setState(() => _isPlayingAudio = !_isPlayingAudio),
                style: IconButton.styleFrom(
                  backgroundColor: _copper,
                  foregroundColor: _ink,
                ),
                icon: Icon(_isPlayingAudio ? Icons.pause : Icons.play_arrow,
                    size: 19),
              ),
              const SizedBox(width: 10),
              const Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Text(
                      'ĐANG KHÁM PHÁ',
                      style: TextStyle(
                          color: _muted,
                          fontSize: 8,
                          letterSpacing: 1.2,
                          fontWeight: FontWeight.w700),
                    ),
                    SizedBox(height: 2),
                    Text(
                      'Âm vang văn minh Đông Sơn',
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      style: TextStyle(
                          color: Colors.white,
                          fontSize: 11,
                          fontWeight: FontWeight.w600),
                    ),
                  ],
                ),
              ),
              const SizedBox(width: 8),
              const Icon(Icons.graphic_eq, color: _copper, size: 20),
            ],
          ),
        ),
      ),
    );
  }
}
