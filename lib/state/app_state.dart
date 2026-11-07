import 'package:flutter/material.dart';

/// Quản lý trạng thái đơn giản của toàn ứng dụng bằng ChangeNotifier
class AppState extends ChangeNotifier {
  String? _confirmedLocation;
  DateTime? _confirmedTime;
  String _confirmationSource = 'chưa xác nhận'; // 'thủ công' hoặc 'QR'

  String? _selectedExhibitId;
  String _selectedExhibitName = 'Trống đồng Đông Sơn (Demo)';

  String? get confirmedLocation => _confirmedLocation;
  DateTime? get confirmedTime => _confirmedTime;
  String get confirmationSource => _confirmationSource;

  String? get selectedExhibitId => _selectedExhibitId;
  String get selectedExhibitName => _selectedExhibitName;

  /// Cập nhật vị trí xác nhận gần nhất
  void updateLocation(String locationName, {bool isQr = false}) {
    _confirmedLocation = locationName;
    _confirmedTime = DateTime.now();
    _confirmationSource = isQr ? 'QR code' : 'thủ công';
    notifyListeners();
  }

  /// Chọn hiện vật đang xem
  void selectExhibit(String id, String name) {
    _selectedExhibitId = id;
    _selectedExhibitName = name;
    notifyListeners();
  }

  /// Khách xác nhận đã đến điểm đích
  void confirmArrivalAt(String locationName) {
    _confirmedLocation = locationName;
    _confirmedTime = DateTime.now();
    _confirmationSource = 'thủ công (đã đến)';
    notifyListeners();
  }
}

/// Provider tự viết bằng InheritedNotifier (không cần thêm thư viện ngoài)
class AppStateScope extends InheritedNotifier<AppState> {
  const AppStateScope({
    super.key,
    required AppState super.notifier,
    required super.child,
  });

  static AppState of(BuildContext context) {
    final scope = context.dependOnInheritedWidgetOfExactType<AppStateScope>();
    assert(scope != null, 'Không tìm thấy AppStateScope trong widget tree');
    return scope!.notifier!;
  }
}

