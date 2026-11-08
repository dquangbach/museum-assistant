# Museum Guide App

Ứng dụng Flutter hỗ trợ tham quan Bảo tàng Đà Nẵng. Danh mục nhóm, mục trưng bày, mô tả và ảnh được tải từ FastAPI/PostgreSQL. Checkpoint xác nhận vị trí vẫn là dữ liệu mẫu trên điện thoại; chưa có sơ đồ chỉ đường thật.

## Chạy backend

Mở Docker Desktop hoặc OrbStack, sau đó từ thư mục gốc dự án:

```bash
docker compose up --build -d
docker compose exec api python -m scripts.import_dataset
```

API mặc định ở `http://localhost:8002`; kiểm tra `http://localhost:8002/health/ready`. Xem [backend/README.md](backend/README.md) để biết thêm về database và import dữ liệu.

## Chạy Flutter

Trên iOS Simulator, `localhost` là máy chạy backend:

```bash
flutter pub get
flutter run -d <IOS_SIMULATOR_ID>
```

Trên iPhone thật, dùng IP LAN của máy chạy backend. Cả iPhone và máy chủ cần ở cùng mạng; thay `IP_CUA_MAY` bằng địa chỉ thật (có thể xem bằng `ipconfig getifaddr en0` trên Mac):

```bash
flutter run -d 00008020-001D045001D8002E --dart-define=API_BASE_URL=http://IP_CUA_MAY:8002
```

Trên Android Emulator, dùng `--dart-define=API_BASE_URL=http://10.0.2.2:8002`. Khi đưa backend lên cloud, dùng URL HTTPS thay cho HTTP LAN. Bản Android debug/profile cho phép HTTP nội bộ; bản release cần HTTPS. Khi iOS hỏi quyền Mạng cục bộ và Camera, hãy cho phép để tải dữ liệu và quét QR.

Trang chủ tải `/api/v1/groups` và `/api/v1/topics`. Chạm một mục để xem mô tả và ảnh từ `/api/v1/topics/{id}` cùng `/api/v1/topics/{id}/assets`.

## Quét QR

Mã QR chủ đề có nội dung ví dụ `museum://topic/TOPIC005`. App gửi nội dung tới `/api/v1/qr/resolve`, sau đó mở chi tiết mục. Mã hiện vật đã xuất bản cũng được phân giải; app mở chủ đề chứa hiện vật đó. Các ảnh QR `exhibit-EX01` đến `EX03` trong `docs/qr-samples` là dữ liệu demo cũ, không có trong database nên không dùng để thử API.

Checkpoint mẫu `museum-demo://checkpoint/CP01` vẫn có thể thử bằng [ảnh QR cửa vào](docs/qr-samples/checkpoint-CP01.png). Checkpoint chỉ được kiểm tra cục bộ, không lưu vào PostgreSQL.
