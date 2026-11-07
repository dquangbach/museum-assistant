import 'package:flutter/material.dart';
import '../state/app_state.dart';
import 'chat_screen.dart';
import 'location_picker_screen.dart';
import 'navigation_screen.dart';

class ExhibitDetailScreen extends StatefulWidget {
  final String exhibitId;
  final String exhibitName;
  final String period;
  final String room;
  final String cabinet;
  final String desc;
  final String symbol;

  const ExhibitDetailScreen({
    super.key,
    required this.exhibitId,
    required this.exhibitName,
    this.period = 'Thời kỳ Tiền sử - Sơ sử',
    required this.room,
    required this.cabinet,
    required this.desc,
    this.symbol = '🏛️',
  });

  @override
  State<ExhibitDetailScreen> createState() => _ExhibitDetailScreenState();
}

class _ExhibitDetailScreenState extends State<ExhibitDetailScreen> {
  bool _isPlayingAudio = false;

  final List<Map<String, String>> _relatedItems = [
    {
      'title': 'Rìu lưỡi xéo đồng',
      'era': 'Khoảng 1000 TCN',
      'icon': '🪓',
    },
    {
      'title': 'Thạp đồng Đào Thịnh',
      'era': 'Khoảng 500 TCN',
      'icon': '🏺',
    },
    {
      'title': 'Khuyên tai hai đầu thú',
      'era': 'Khoảng 200 TCN',
      'icon': '💍',
    },
  ];

  @override
  Widget build(BuildContext context) {
    final appState = AppStateScope.of(context);

    return Scaffold(
      backgroundColor: const Color(0xFF121212),
      body: Stack(
        children: [
          SingleChildScrollView(
            padding: const EdgeInsets.only(bottom: 110),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Top Header với hình hiện vật làm tâm điểm (Museo Artwork Hero)
                Container(
                  width: double.infinity,
                  decoration: const BoxDecoration(
                    color: Color(0xFF181818),
                    borderRadius: BorderRadius.only(
                      bottomLeft: Radius.circular(32),
                      bottomRight: Radius.circular(32),
                    ),
                    border: Border(
                      bottom: BorderSide(color: Color(0xFF2A2A2A)),
                    ),
                  ),
                  child: SafeArea(
                    bottom: false,
                    child: Padding(
                      padding: const EdgeInsets.fromLTRB(20, 12, 20, 24),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              IconButton(
                                style: IconButton.styleFrom(
                                  backgroundColor: const Color(0xFF242424),
                                  shape: const CircleBorder(),
                                  side: const BorderSide(
                                      color: Color(0xFF333333)),
                                ),
                                icon: const Icon(Icons.arrow_back,
                                    color: Colors.white, size: 20),
                                onPressed: () => Navigator.pop(context),
                              ),
                              Container(
                                padding: const EdgeInsets.symmetric(
                                    horizontal: 12, vertical: 6),
                                decoration: BoxDecoration(
                                  color: const Color(0xFF242424),
                                  borderRadius: BorderRadius.circular(16),
                                  border: Border.all(
                                      color: const Color(0xFF333333)),
                                ),
                                child: Text(
                                  widget.room,
                                  style: const TextStyle(
                                    color: Color(0xFFEAC0A2),
                                    fontSize: 11,
                                    fontWeight: FontWeight.w600,
                                  ),
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 16),

                          // Khung trưng bày hiện vật nổi bật trung tâm
                          Center(
                            child: Container(
                              width: 240,
                              height: 190,
                              decoration: BoxDecoration(
                                color: const Color(0xFF121212),
                                borderRadius: BorderRadius.circular(24),
                                border:
                                    Border.all(color: const Color(0xFF333333)),
                                boxShadow: [
                                  BoxShadow(
                                    color:
                                        const Color(0xFFEAC0A2).withAlpha(20),
                                    blurRadius: 30,
                                    offset: const Offset(0, 10),
                                  ),
                                ],
                              ),
                              child: widget.exhibitId == 'EX01'
                                  ? ClipRRect(
                                      borderRadius: BorderRadius.circular(23),
                                      child: Image.asset(
                                        'assets/images/dong-son-drum.png',
                                        width: 240,
                                        height: 190,
                                        fit: BoxFit.cover,
                                        alignment: const Alignment(0, 0.46),
                                      ),
                                    )
                                  : Column(
                                      mainAxisAlignment:
                                          MainAxisAlignment.center,
                                      children: [
                                        Text(widget.symbol,
                                            style:
                                                const TextStyle(fontSize: 70)),
                                        const SizedBox(height: 8),
                                        Container(
                                          padding: const EdgeInsets.symmetric(
                                              horizontal: 10, vertical: 3),
                                          decoration: BoxDecoration(
                                            color: const Color(0xFF242424),
                                            borderRadius:
                                                BorderRadius.circular(8),
                                          ),
                                          child: Text(
                                            widget.cabinet,
                                            style: const TextStyle(
                                              color: Color(0xFF8E8E93),
                                              fontSize: 10,
                                              fontWeight: FontWeight.bold,
                                            ),
                                          ),
                                        ),
                                      ],
                                    ),
                            ),
                          ),
                          const SizedBox(height: 20),

                          const Text(
                            'BẢO VẬT QUỐC GIA',
                            style: TextStyle(
                              fontSize: 10,
                              fontWeight: FontWeight.w800,
                              letterSpacing: 1.5,
                              color: Color(0xFF8E8E93),
                            ),
                          ),
                          const SizedBox(height: 4),
                          Text(
                            widget.exhibitName,
                            style: const TextStyle(
                              fontSize: 26,
                              fontFamily: 'serif',
                              fontWeight: FontWeight.w500,
                              color: Colors.white,
                              height: 1.1,
                            ),
                          ),
                          const SizedBox(height: 4),
                          Text(
                            widget.period,
                            style: const TextStyle(
                              fontSize: 13,
                              color: Color(0xFFEAC0A2),
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                ),
                const SizedBox(height: 20),

                // Nội dung chi tiết & Trình phát Audio kiểu Museo
                Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 20),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      // Trình phát âm thanh kiểu Museo Player
                      Container(
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
                                GestureDetector(
                                  onTap: () {
                                    setState(() {
                                      _isPlayingAudio = !_isPlayingAudio;
                                    });
                                  },
                                  child: Container(
                                    width: 44,
                                    height: 44,
                                    decoration: const BoxDecoration(
                                      color: Color(0xFFEAC0A2),
                                      shape: BoxShape.circle,
                                    ),
                                    child: Icon(
                                      _isPlayingAudio
                                          ? Icons.pause
                                          : Icons.play_arrow,
                                      color: const Color(0xFF121212),
                                      size: 22,
                                    ),
                                  ),
                                ),
                                const SizedBox(width: 14),
                                Expanded(
                                  child: Column(
                                    crossAxisAlignment:
                                        CrossAxisAlignment.start,
                                    children: [
                                      const Text(
                                        'THUYẾT MINH CHUYÊN GIA',
                                        style: TextStyle(
                                          fontSize: 9,
                                          fontWeight: FontWeight.w800,
                                          letterSpacing: 1.5,
                                          color: Color(0xFF8E8E93),
                                        ),
                                      ),
                                      const SizedBox(height: 2),
                                      Text(
                                        'Âm vang văn minh Đông Sơn',
                                        style: const TextStyle(
                                          fontSize: 14,
                                          fontWeight: FontWeight.bold,
                                          color: Colors.white,
                                        ),
                                      ),
                                    ],
                                  ),
                                ),
                                Text(
                                  _isPlayingAudio ? '01:24' : '03:10',
                                  style: const TextStyle(
                                    color: Color(0xFF8E8E93),
                                    fontSize: 12,
                                    fontWeight: FontWeight.w600,
                                  ),
                                ),
                              ],
                            ),
                            const SizedBox(height: 12),
                            // Thanh tiến trình phát
                            ClipRRect(
                              borderRadius: BorderRadius.circular(4),
                              child: LinearProgressIndicator(
                                value: _isPlayingAudio ? 0.45 : 0.0,
                                backgroundColor: const Color(0xFF2A2A2A),
                                valueColor: const AlwaysStoppedAnimation<Color>(
                                    Color(0xFFEAC0A2)),
                                minHeight: 4,
                              ),
                            ),
                          ],
                        ),
                      ),
                      const SizedBox(height: 24),

                      // Mô tả hiện vật
                      const Text(
                        'Câu chuyện di sản',
                        style: TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.w800,
                          color: Colors.white,
                        ),
                      ),
                      const SizedBox(height: 8),
                      Text(
                        widget.desc,
                        style: const TextStyle(
                          fontSize: 14,
                          color: Color(0xFFB0B3BA),
                          height: 1.6,
                        ),
                      ),
                      const SizedBox(height: 16),

                      // Nguồn hồ sơ khoa học
                      Container(
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          color: const Color(0xFF1A1A1A),
                          borderRadius: BorderRadius.circular(14),
                          border: Border.all(color: const Color(0xFF2A2A2A)),
                        ),
                        child: Row(
                          children: [
                            const Icon(Icons.verified_outlined,
                                size: 16, color: Color(0xFFEAC0A2)),
                            const SizedBox(width: 8),
                            Expanded(
                              child: Text(
                                'Nguồn: Hồ sơ hiện vật Bảo tàng Lịch sử (Demo)',
                                style: const TextStyle(
                                  fontSize: 11,
                                  color: Color(0xFF8E8E93),
                                  fontStyle: FontStyle.italic,
                                ),
                              ),
                            ),
                          ],
                        ),
                      ),
                      const SizedBox(height: 24),

                      // Hiện vật cùng thời kỳ
                      const Text(
                        'Bộ sưu tập cùng thời kỳ',
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.w800,
                          color: Colors.white,
                        ),
                      ),
                      const SizedBox(height: 12),
                      SingleChildScrollView(
                        scrollDirection: Axis.horizontal,
                        child: Row(
                          children: _relatedItems.map((item) {
                            return Container(
                              width: 140,
                              margin: const EdgeInsets.only(right: 12),
                              padding: const EdgeInsets.all(12),
                              decoration: BoxDecoration(
                                color: const Color(0xFF1A1A1A),
                                borderRadius: BorderRadius.circular(18),
                                border:
                                    Border.all(color: const Color(0xFF2A2A2A)),
                              ),
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.center,
                                children: [
                                  Container(
                                    width: 50,
                                    height: 50,
                                    decoration: BoxDecoration(
                                      color: const Color(0xFF242424),
                                      borderRadius: BorderRadius.circular(14),
                                    ),
                                    child: Center(
                                      child: Text(item['icon']!,
                                          style: const TextStyle(fontSize: 24)),
                                    ),
                                  ),
                                  const SizedBox(height: 8),
                                  Text(
                                    item['title']!,
                                    style: const TextStyle(
                                      fontSize: 12,
                                      fontWeight: FontWeight.bold,
                                      color: Colors.white,
                                    ),
                                    textAlign: TextAlign.center,
                                    maxLines: 2,
                                    overflow: TextOverflow.ellipsis,
                                  ),
                                  const SizedBox(height: 4),
                                  Text(
                                    item['era']!,
                                    style: const TextStyle(
                                      fontSize: 10,
                                      color: Color(0xFF8E8E93),
                                    ),
                                  ),
                                ],
                              ),
                            );
                          }).toList(),
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),

          // Thanh nút điều hướng cố định phía dưới màn hình với nút Copper
          Positioned(
            left: 20,
            right: 20,
            bottom: 20,
            child: Row(
              children: [
                // Nút Hỏi đáp
                Container(
                  width: 54,
                  height: 54,
                  decoration: BoxDecoration(
                    color: const Color(0xFF1A1A1A),
                    shape: BoxShape.circle,
                    border: Border.all(color: const Color(0xFF2A2A2A)),
                  ),
                  child: IconButton(
                    icon: const Icon(Icons.chat_bubble_outline,
                        color: Color(0xFFEAC0A2)),
                    tooltip: 'Hỏi đáp hiện vật',
                    onPressed: () {
                      Navigator.push(
                        context,
                        MaterialPageRoute(
                          builder: (_) => ChatScreen(
                            exhibitId: widget.exhibitId,
                            exhibitName: widget.exhibitName,
                          ),
                        ),
                      );
                    },
                  ),
                ),
                const SizedBox(width: 12),
                // Nút Dẫn đường chính màu Copper/Champagne sang trọng
                Expanded(
                  child: GestureDetector(
                    onTap: () {
                      if (appState.confirmedLocation == null) {
                        ScaffoldMessenger.of(context).showSnackBar(
                          const SnackBar(
                            content: Text(
                                'Vui lòng chọn vị trí xuất phát trước khi dẫn đường.'),
                          ),
                        );
                        Navigator.push(
                          context,
                          MaterialPageRoute(
                            builder: (_) => LocationPickerScreen(
                              nextScreenAfterSelection: NavigationScreen(
                                destinationName: widget.exhibitName,
                                cabinet: widget.cabinet,
                              ),
                            ),
                          ),
                        );
                      } else {
                        Navigator.push(
                          context,
                          MaterialPageRoute(
                            builder: (_) => NavigationScreen(
                              destinationName: widget.exhibitName,
                              cabinet: widget.cabinet,
                            ),
                          ),
                        );
                      }
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
                          Icon(Icons.directions,
                              color: Color(0xFF121212), size: 20),
                          SizedBox(width: 8),
                          Text(
                            'Chỉ đường tới hiện vật',
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
        ],
      ),
    );
  }
}
