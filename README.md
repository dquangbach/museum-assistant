# Museum Guide App

Ứng dụng Flutter demo hỗ trợ xem hiện vật, quét QR, xác định điểm đứng và chỉ đường trong bảo tàng.

## Chạy trên iPhone

```bash
flutter pub get
flutter run --release -d 00008020-001D045001D8002E
```

Khi mở camera lần đầu, hãy cho phép ứng dụng truy cập Camera.

## Thử quét QR hiện vật

1. Mở một ảnh trong [docs/qr-samples](docs/qr-samples) trên máy tính hoặc in ra giấy.
2. Trong app, nhấn **Quét mã tại bảo tàng** hoặc **Mở camera quét QR** ở màn chọn vị trí.
3. Đưa mã vào khung. QR hiện vật mở trang mô tả; QR điểm đứng cập nhật vị trí hiện tại.

| Ảnh mẫu | Nội dung QR | Kết quả |
| --- | --- | --- |
| [Trống đồng Đông Sơn](docs/qr-samples/exhibit-EX01.png) | `museum-demo://exhibit/EX01` | Mở chi tiết trống đồng |
| [Tượng Phật Bà Quan Âm](docs/qr-samples/exhibit-EX02.png) | `museum-demo://exhibit/EX02` | Mở chi tiết tượng |
| [Bình gốm hoa lam](docs/qr-samples/exhibit-EX03.png) | `museum-demo://exhibit/EX03` | Mở chi tiết bình gốm |
| [Cửa vào sảnh chính](docs/qr-samples/checkpoint-CP01.png) | `museum-demo://checkpoint/CP01` | Xác nhận điểm đứng |

Dữ liệu đang nằm trong [lib/data/museum_catalog.dart](lib/data/museum_catalog.dart). App chỉ nhận những ID có trong danh mục này. Backend FastAPI đã có tại [backend/](backend/README.md). Flutter hiện vẫn tra danh mục cục bộ; bước tích hợp tiếp theo là gọi API để lấy dữ liệu thật.

## Backend FastAPI

Xem cấu hình và hướng dẫn tại [backend/README.md](backend/README.md). Từ thư mục gốc, mở Docker Desktop hoặc OrbStack rồi chạy:

```bash
docker compose up --build -d
docker compose exec api python -m scripts.import_dataset
```

Swagger: http://localhost:8002/docs. Backend lưu dữ liệu trong PostgreSQL, đọc ảnh từ Dataset được mount chỉ đọc. Các thao tác quản trị dùng X-Admin-Key, cấu hình tại .env gốc; không đưa khóa này vào app khách tham quan.
