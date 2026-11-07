import 'package:flutter/material.dart';
import '../data/museum_catalog.dart';
import '../state/app_state.dart';
import 'exhibit_detail_screen.dart';
import 'qr_scanner_screen.dart';

class LocationPickerScreen extends StatefulWidget {
  final Widget? nextScreenAfterSelection;

  const LocationPickerScreen({super.key, this.nextScreenAfterSelection});

  @override
  State<LocationPickerScreen> createState() => _LocationPickerScreenState();
}

class _LocationPickerScreenState extends State<LocationPickerScreen> {
  final List<Map<String, String>> _checkpoints = museumCheckpoints;

  Future<void> _scanQr() async {
    final result = await Navigator.push<MuseumQrResult>(
      context,
      MaterialPageRoute(builder: (_) => const QrScannerScreen()),
    );
    if (!mounted || result == null) return;

    if (result.kind == MuseumQrKind.checkpoint) {
      final checkpoint = findMuseumCheckpoint(result.id);
      if (checkpoint != null) _onSelectLocation(checkpoint['name']!, true);
      return;
    }

    final exhibit = findMuseumExhibit(result.id);
    if (exhibit == null) return;
    AppStateScope.of(context).selectExhibit(exhibit['id']!, exhibit['name']!);
    Navigator.pushReplacement(
      context,
      MaterialPageRoute(
        builder: (_) => ExhibitDetailScreen(
          exhibitId: exhibit['id']!,
          exhibitName: exhibit['name']!,
          period: exhibit['period']!,
          room: exhibit['room']!,
          cabinet: exhibit['cabinet']!,
          desc: exhibit['desc']!,
          symbol: exhibit['symbol']!,
        ),
      ),
    );
  }

  void _onSelectLocation(String name, bool isQr) {
    final appState = AppStateScope.of(context);
    appState.updateLocation(name, isQr: isQr);

    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        backgroundColor: const Color(0xFF1E1E1E),
        content: Text(
          'Đã xác nhận vị trí: $name (${isQr ? "qua QR" : "thủ công"})',
          style: const TextStyle(color: Color(0xFFEAC0A2)),
        ),
        duration: const Duration(seconds: 2),
      ),
    );

    if (widget.nextScreenAfterSelection != null) {
      Navigator.pushReplacement(
        context,
        MaterialPageRoute(builder: (_) => widget.nextScreenAfterSelection!),
      );
    } else {
      Navigator.pop(context);
    }
  }

  @override
  Widget build(BuildContext context) {
    final appState = AppStateScope.of(context);

    return Scaffold(
      backgroundColor: const Color(0xFF121212),
      appBar: AppBar(
        title: const Text('Xác nhận vị trí'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => Navigator.pop(context),
        ),
      ),
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.all(20),
          children: [
            // Quét QR hiện vật hoặc điểm đứng bằng camera.
            Container(
              decoration: BoxDecoration(
                color: const Color(0xFF1A1A1A),
                borderRadius: BorderRadius.circular(26),
                border: Border.all(color: const Color(0xFF2A2A2A)),
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withAlpha(50),
                    blurRadius: 18,
                    offset: const Offset(0, 8),
                  ),
                ],
              ),
              child: Padding(
                padding: const EdgeInsets.all(22.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        const Text(
                          'QUÉT MÃ BẢO TÀNG',
                          style: TextStyle(
                            fontSize: 10,
                            fontWeight: FontWeight.w800,
                            letterSpacing: 1.5,
                            color: Color(0xFFEAC0A2),
                          ),
                        ),
                        Container(
                          padding: const EdgeInsets.symmetric(
                              horizontal: 8, vertical: 2),
                          decoration: BoxDecoration(
                            color: const Color(0xFF242424),
                            borderRadius: BorderRadius.circular(8),
                          ),
                          child: const Text(
                            'Camera',
                            style: TextStyle(
                                color: Color(0xFF8E8E93), fontSize: 10),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 8),
                    const Text(
                      'Quét QR hiện vật',
                      style: TextStyle(
                        fontSize: 20,
                        fontWeight: FontWeight.w900,
                        color: Colors.white,
                        letterSpacing: -0.3,
                      ),
                    ),
                    const SizedBox(height: 6),
                    const Text(
                      'Quét mã cạnh hiện vật để xem mô tả, hoặc quét mã tại cửa phòng để xác định vị trí.',
                      style: TextStyle(
                        fontSize: 12,
                        color: Color(0xFF8E8E93),
                        height: 1.4,
                      ),
                    ),
                    const SizedBox(height: 18),
                    // Mở camera quét QR.
                    GestureDetector(
                      onTap: _scanQr,
                      child: Container(
                        padding: const EdgeInsets.symmetric(
                            horizontal: 20, vertical: 12),
                        decoration: BoxDecoration(
                          color: const Color(0xFFEAC0A2),
                          borderRadius: BorderRadius.circular(20),
                        ),
                        child: Row(
                          mainAxisSize: MainAxisSize.min,
                          children: const [
                            Icon(Icons.qr_code_scanner,
                                size: 18, color: Color(0xFF121212)),
                            SizedBox(width: 8),
                            Text(
                              'Mở camera quét QR',
                              style: TextStyle(
                                fontSize: 13,
                                fontWeight: FontWeight.bold,
                                color: Color(0xFF121212),
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 28),

            const Text(
              'HOẶC CHỌN ĐIỂM MỐC THỦ CÔNG',
              style: TextStyle(
                fontSize: 11,
                fontWeight: FontWeight.w800,
                letterSpacing: 1.5,
                color: Color(0xFF8E8E93),
              ),
            ),
            const SizedBox(height: 12),

            // Danh sách các điểm mốc phong cách Dark-Luxury
            ..._checkpoints.map((cp) {
              final isCurrent = appState.confirmedLocation == cp['name'];
              return Container(
                margin: const EdgeInsets.only(bottom: 12),
                decoration: BoxDecoration(
                  color: const Color(0xFF1A1A1A),
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(
                    color: isCurrent
                        ? const Color(0xFFEAC0A2)
                        : const Color(0xFF2A2A2A),
                    width: isCurrent ? 2 : 1,
                  ),
                ),
                child: ListTile(
                  contentPadding:
                      const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
                  leading: Container(
                    width: 44,
                    height: 44,
                    decoration: BoxDecoration(
                      color: isCurrent
                          ? const Color(0xFFEAC0A2)
                          : const Color(0xFF242424),
                      borderRadius: BorderRadius.circular(14),
                    ),
                    child: Center(
                      child: Text(
                        cp['icon'] ?? '📍',
                        style: const TextStyle(fontSize: 20),
                      ),
                    ),
                  ),
                  title: Text(
                    cp['name']!,
                    style: TextStyle(
                      fontSize: 14,
                      fontWeight: isCurrent ? FontWeight.w800 : FontWeight.w600,
                      color: isCurrent ? const Color(0xFFEAC0A2) : Colors.white,
                    ),
                  ),
                  subtitle: Text(
                    cp['desc']!,
                    style: const TextStyle(
                      fontSize: 12,
                      color: Color(0xFF8E8E93),
                    ),
                  ),
                  trailing: isCurrent
                      ? const Icon(Icons.check_circle, color: Color(0xFFEAC0A2))
                      : const Icon(Icons.arrow_forward_ios,
                          size: 14, color: Color(0xFF555555)),
                  onTap: () {
                    _onSelectLocation(cp['name']!, false);
                  },
                ),
              );
            }),
          ],
        ),
      ),
    );
  }
}
