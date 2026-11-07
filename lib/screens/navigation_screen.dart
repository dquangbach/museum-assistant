import 'package:flutter/material.dart';
import '../state/app_state.dart';
import 'location_picker_screen.dart';

class NavigationScreen extends StatelessWidget {
  final String destinationName;
  final String cabinet;

  const NavigationScreen({
    super.key,
    required this.destinationName,
    required this.cabinet,
  });

  @override
  Widget build(BuildContext context) {
    final appState = AppStateScope.of(context);
    final startLocation = appState.confirmedLocation ?? 'Chưa xác định';
    final isAlreadyThere = startLocation.contains(destinationName);

    final demoSteps = [
      'Từ $startLocation, đi thẳng khoảng 10m theo hành lang sảnh chính.',
      'Rẽ phải vào cửa vòm Phòng 1 - Cổ vật.',
      'Đi tiếp 5m tới $cabinet. Hiện vật nằm ngay tầm mắt phía trước.',
    ];

    return Scaffold(
      backgroundColor: const Color(0xFF121212),
      appBar: AppBar(
        title: const Text('Chỉ dẫn đường đi'),
        actions: [
          TextButton.icon(
            icon: const Icon(Icons.edit_location_alt, size: 16, color: Color(0xFFEAC0A2)),
            label: const Text(
              'Đổi điểm đầu',
              style: TextStyle(
                color: Color(0xFFEAC0A2),
                fontWeight: FontWeight.bold,
                fontSize: 12,
              ),
            ),
            onPressed: () {
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (_) => LocationPickerScreen(
                    nextScreenAfterSelection: NavigationScreen(
                      destinationName: destinationName,
                      cabinet: cabinet,
                    ),
                  ),
                ),
              );
            },
          ),
        ],
      ),
      body: SafeArea(
        child: Column(
          children: [
            // Thẻ tóm tắt lộ trình phong cách Dark-Luxury
            Container(
              margin: const EdgeInsets.fromLTRB(20, 8, 20, 16),
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: const Color(0xFF1A1A1A),
                borderRadius: BorderRadius.circular(22),
                border: Border.all(color: const Color(0xFF2A2A2A)),
              ),
              child: Column(
                children: [
                  Row(
                    children: [
                      Container(
                        width: 10,
                        height: 10,
                        decoration: const BoxDecoration(
                          color: Color(0xFF60A5FA),
                          shape: BoxShape.circle,
                        ),
                      ),
                      const SizedBox(width: 10),
                      const Text(
                        'XUẤT PHÁT: ',
                        style: TextStyle(
                          color: Color(0xFF8E8E93),
                          fontSize: 10,
                          fontWeight: FontWeight.w800,
                          letterSpacing: 1.2,
                        ),
                      ),
                      Expanded(
                        child: Text(
                          startLocation,
                          style: const TextStyle(
                            color: Colors.white,
                            fontSize: 13,
                            fontWeight: FontWeight.w600,
                          ),
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),
                    ],
                  ),
                  const Padding(
                    padding: EdgeInsets.only(left: 4, top: 4, bottom: 4),
                    child: Align(
                      alignment: Alignment.centerLeft,
                      child: SizedBox(
                        height: 12,
                        child: VerticalDivider(color: Color(0xFF333333), thickness: 1.5),
                      ),
                    ),
                  ),
                  Row(
                    children: [
                      Container(
                        width: 10,
                        height: 10,
                        decoration: const BoxDecoration(
                          color: Color(0xFFEAC0A2),
                          shape: BoxShape.circle,
                        ),
                      ),
                      const SizedBox(width: 10),
                      const Text(
                        'ĐÍCH ĐẾN: ',
                        style: TextStyle(
                          color: Color(0xFF8E8E93),
                          fontSize: 10,
                          fontWeight: FontWeight.w800,
                          letterSpacing: 1.2,
                        ),
                      ),
                      Expanded(
                        child: Text(
                          '$destinationName ($cabinet)',
                          style: const TextStyle(
                            color: Color(0xFFEAC0A2),
                            fontSize: 13,
                            fontWeight: FontWeight.bold,
                          ),
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),

            // Khu vực bản đồ 2D mô phỏng
            Expanded(
              flex: 4,
              child: Container(
                width: double.infinity,
                margin: const EdgeInsets.symmetric(horizontal: 20),
                decoration: BoxDecoration(
                  color: const Color(0xFF181818),
                  borderRadius: BorderRadius.circular(26),
                  border: Border.all(color: const Color(0xFF2A2A2A)),
                ),
                child: isAlreadyThere
                    ? Center(
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: const [
                            Icon(Icons.check_circle_outline, color: Color(0xFFEAC0A2), size: 52),
                            SizedBox(height: 12),
                            Text(
                              'Bạn đang ở điểm đến!',
                              style: TextStyle(
                                fontSize: 16,
                                fontWeight: FontWeight.w800,
                                color: Color(0xFFEAC0A2),
                              ),
                            ),
                          ],
                        ),
                      )
                    : Stack(
                        alignment: Alignment.center,
                        children: [
                          Padding(
                            padding: const EdgeInsets.all(24.0),
                            child: Column(
                              mainAxisAlignment: MainAxisAlignment.center,
                              children: [
                                Container(
                                  width: 76,
                                  height: 76,
                                  decoration: BoxDecoration(
                                    color: const Color(0xFF222222),
                                    borderRadius: BorderRadius.circular(22),
                                    border: Border.all(color: const Color(0xFF333333)),
                                  ),
                                  child: const Center(
                                    child: Icon(
                                      Icons.map_outlined,
                                      size: 38,
                                      color: Color(0xFFEAC0A2),
                                    ),
                                  ),
                                ),
                                const SizedBox(height: 14),
                                const Text(
                                  'Sơ đồ không gian Tầng 1',
                                  style: TextStyle(
                                    fontSize: 15,
                                    fontWeight: FontWeight.w800,
                                    color: Colors.white,
                                  ),
                                ),
                                const SizedBox(height: 4),
                                const Text(
                                  'Ước tính: ~25 mét • Thời gian đi bộ: ~1 phút',
                                  style: TextStyle(
                                    fontSize: 12,
                                    color: Color(0xFF8E8E93),
                                  ),
                                ),
                              ],
                            ),
                          ),
                          // Pin điểm bắt đầu
                          Positioned(
                            left: 20,
                            bottom: 20,
                            child: Container(
                              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                              decoration: BoxDecoration(
                                color: const Color(0xFF242424),
                                borderRadius: BorderRadius.circular(12),
                                border: Border.all(color: const Color(0xFF333333)),
                              ),
                              child: const Row(
                                mainAxisSize: MainAxisSize.min,
                                children: [
                                  Icon(Icons.person_pin, color: Colors.white, size: 14),
                                  SizedBox(width: 4),
                                  Text(
                                    'Điểm đầu',
                                    style: TextStyle(color: Colors.white, fontSize: 10, fontWeight: FontWeight.bold),
                                  ),
                                ],
                              ),
                            ),
                          ),
                          // Pin điểm đến
                          Positioned(
                            right: 20,
                            top: 20,
                            child: Container(
                              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                              decoration: BoxDecoration(
                                color: const Color(0xFFEAC0A2),
                                borderRadius: BorderRadius.circular(12),
                              ),
                              child: const Row(
                                mainAxisSize: MainAxisSize.min,
                                children: [
                                  Icon(Icons.flag, color: Color(0xFF121212), size: 14),
                                  SizedBox(width: 4),
                                  Text(
                                    'Đích đến',
                                    style: TextStyle(color: Color(0xFF121212), fontSize: 10, fontWeight: FontWeight.bold),
                                  ),
                                ],
                              ),
                            ),
                          ),
                        ],
                      ),
              ),
            ),
            const SizedBox(height: 16),

            // Các bước di chuyển
            Expanded(
              flex: 3,
              child: ListView(
                padding: const EdgeInsets.symmetric(horizontal: 20),
                children: [
                  const Text(
                    'LỘ TRÌNH TỪNG BƯỚC',
                    style: TextStyle(
                      fontSize: 11,
                      fontWeight: FontWeight.w800,
                      letterSpacing: 1.5,
                      color: Color(0xFF8E8E93),
                    ),
                  ),
                  const SizedBox(height: 10),
                  if (isAlreadyThere)
                    const Padding(
                      padding: EdgeInsets.symmetric(vertical: 8),
                      child: Text(
                        'Bạn đã ở ngay cạnh hiện vật này.',
                        style: TextStyle(color: Color(0xFF8E8E93)),
                      ),
                    )
                  else
                    ...demoSteps.asMap().entries.map((entry) {
                      final idx = entry.key + 1;
                      final text = entry.value;
                      return Container(
                        margin: const EdgeInsets.only(bottom: 8),
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          color: const Color(0xFF1A1A1A),
                          borderRadius: BorderRadius.circular(16),
                          border: Border.all(color: const Color(0xFF2A2A2A)),
                        ),
                        child: Row(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Container(
                              width: 22,
                              height: 22,
                              decoration: const BoxDecoration(
                                color: Color(0xFFEAC0A2),
                                shape: BoxShape.circle,
                              ),
                              child: Center(
                                child: Text(
                                  '$idx',
                                  style: const TextStyle(
                                    fontSize: 11,
                                    color: Color(0xFF121212),
                                    fontWeight: FontWeight.bold,
                                  ),
                                ),
                              ),
                            ),
                            const SizedBox(width: 12),
                            Expanded(
                              child: Text(
                                text,
                                style: const TextStyle(
                                  fontSize: 13,
                                  color: Color(0xFFD1D5DB),
                                  height: 1.4,
                                ),
                              ),
                            ),
                          ],
                        ),
                      );
                    }),
                ],
              ),
            ),

            // Nút "Tôi đã đến nơi" màu Copper
            Padding(
              padding: const EdgeInsets.fromLTRB(20, 8, 20, 16),
              child: GestureDetector(
                onTap: () {
                  appState.confirmArrivalAt('$destinationName ($cabinet)');
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(
                      backgroundColor: const Color(0xFF1E1E1E),
                      content: Text(
                        'Đã cập nhật vị trí xác nhận: $destinationName',
                        style: const TextStyle(color: Color(0xFFEAC0A2)),
                      ),
                      duration: const Duration(seconds: 2),
                    ),
                  );
                  Navigator.pop(context);
                },
                child: Container(
                  height: 54,
                  decoration: BoxDecoration(
                    color: const Color(0xFFEAC0A2),
                    borderRadius: BorderRadius.circular(28),
                    boxShadow: [
                      BoxShadow(
                        color: const Color(0xFFEAC0A2).withAlpha(40),
                        blurRadius: 16,
                        offset: const Offset(0, 6),
                      ),
                    ],
                  ),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: const [
                      Icon(Icons.check, color: Color(0xFF121212), size: 20),
                      SizedBox(width: 8),
                      Text(
                        'Tôi đã đến nơi',
                        style: TextStyle(
                          color: Color(0xFF121212),
                          fontSize: 15,
                          fontWeight: FontWeight.w900,
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
