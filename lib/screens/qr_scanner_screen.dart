import 'package:flutter/material.dart';
import 'package:mobile_scanner/mobile_scanner.dart';

import '../data/museum_catalog.dart';

/// Chỉ đọc và kiểm tra QR; màn gọi quyết định mở hiện vật hay cập nhật vị trí.
class QrScannerScreen extends StatefulWidget {
  const QrScannerScreen({super.key});

  @override
  State<QrScannerScreen> createState() => _QrScannerScreenState();
}

class _QrScannerScreenState extends State<QrScannerScreen> {
  final MobileScannerController _controller = MobileScannerController(
    formats: [BarcodeFormat.qrCode],
    detectionSpeed: DetectionSpeed.noDuplicates,
  );

  bool _completed = false;
  DateTime? _lastInvalidAt;

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  void _onDetect(BarcodeCapture capture) {
    if (_completed || !mounted) return;

    String? invalidValue;
    for (final barcode in capture.barcodes) {
      final rawValue = barcode.rawValue;
      if (rawValue == null || rawValue.isEmpty) continue;

      final result = resolveMuseumQr(rawValue);
      if (result != null) {
        _completed = true;
        Navigator.of(context).pop(result);
        return;
      }
      invalidValue = rawValue;
    }

    if (invalidValue == null) return;
    final now = DateTime.now();
    if (_lastInvalidAt != null &&
        now.difference(_lastInvalidAt!) < const Duration(seconds: 3)) {
      return;
    }
    _lastInvalidAt = now;
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content:
            Text('Mã QR này chưa có trong dữ liệu bảo tàng. Hãy thử mã khác.'),
        duration: Duration(seconds: 2),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF121212),
      appBar: AppBar(title: const Text('Quét mã QR')),
      body: Stack(
        fit: StackFit.expand,
        children: [
          MobileScanner(
            controller: _controller,
            onDetect: _onDetect,
            errorBuilder: (context, error) => const Center(
              child: Padding(
                padding: EdgeInsets.all(28),
                child: Text(
                  'Không mở được camera. Hãy cấp quyền Camera cho ứng dụng trong Cài đặt của điện thoại rồi thử lại.',
                  textAlign: TextAlign.center,
                  style: TextStyle(color: Colors.white, fontSize: 14),
                ),
              ),
            ),
          ),
          IgnorePointer(
            child: Column(
              children: [
                Container(
                  width: double.infinity,
                  padding: const EdgeInsets.fromLTRB(24, 28, 24, 22),
                  color: const Color(0xCC121212),
                  child: const Column(
                    children: [
                      Text(
                        'Đưa mã QR vào khung',
                        style: TextStyle(
                          color: Colors.white,
                          fontFamily: 'serif',
                          fontSize: 24,
                        ),
                      ),
                      SizedBox(height: 6),
                      Text(
                        'Quét mã cạnh hiện vật để xem câu chuyện của nó.',
                        textAlign: TextAlign.center,
                        style:
                            TextStyle(color: Color(0xFFD1D1D1), fontSize: 12),
                      ),
                    ],
                  ),
                ),
                Expanded(
                  child: Center(
                    child: Container(
                      width: 258,
                      height: 258,
                      decoration: BoxDecoration(
                        border: Border.all(
                          color: const Color(0xFFEAC0A2),
                          width: 2,
                        ),
                        borderRadius: BorderRadius.circular(22),
                      ),
                      child: const Center(
                        child: Icon(
                          Icons.qr_code_2,
                          color: Color(0x66FFFFFF),
                          size: 74,
                        ),
                      ),
                    ),
                  ),
                ),
                Container(
                  width: double.infinity,
                  padding: const EdgeInsets.fromLTRB(24, 22, 24, 38),
                  color: const Color(0xCC121212),
                  child: const Text(
                    'Bạn cũng có thể quét QR tại cửa phòng để xác định vị trí đứng.',
                    textAlign: TextAlign.center,
                    style: TextStyle(color: Color(0xFFEAC0A2), fontSize: 12),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
