# Backend Bảo tàng Đà Nẵng

FastAPI + SQLAlchemy + PostgreSQL, migration bằng Alembic. Flutter gọi API qua HTTP. Backend hiện có API danh mục, ảnh, hiện vật và tra cứu QR; chưa có đồ thị chỉ đường vì nguồn chưa có tọa độ/lối đi thực tế.

## Chạy bằng Docker

Mở Docker Desktop hoặc OrbStack trước. Từ thư mục gốc dự án:

```bash
cp -n .env.example .env
docker compose up --build -d
docker compose exec api python -m scripts.import_dataset
```

Nếu `.env` đã tồn tại, bổ sung biến từ `.env.example` thay vì ghi đè. Compose mặc định dùng thông số phát triển; có thể chạy với mặc định mà không cần tạo `.env`. PostgreSQL lưu trong volume `postgres_data`, không mở cổng database ra máy chủ. Cổng API trên máy mặc định là 8002 (trong container là 8000), có thể đổi bằng API_PORT. API đợi PostgreSQL healthy và service migration hoàn thành rồi mới khởi chạy. Dataset được mount chỉ đọc; import không sao chép hay chỉnh sửa ảnh.

- Swagger: http://localhost:8002/docs
- Liveness: http://localhost:8002/health/live
- Readiness/database migration: http://localhost:8002/health/ready

```bash
docker compose logs -f api
docker compose down
```

`down` giữ volume database. Sau khi thêm migration mới, chạy `docker compose run --rm migrate` rồi khởi động lại API. Các lệnh Compose được chạy từ thư mục gốc, không phải backend/.

## Dữ liệu và API

Importer đọc `groups.json`, `topics.json`, `assets.json`, `topic_assets.json` từ `Dataset/metadata/`; kiểm tra khóa, quan hệ, đường dẫn, kích thước và SHA-256 của ảnh trước khi ghi. Cả lần nhập nằm trong một transaction. Chạy lại sẽ cập nhật theo ID (upsert), không tạo bản trùng và không xóa các bản ghi vắng mặt trong JSON. Thay đổi JSON là thay đổi nguồn nhập cho các trường tương ứng.

Nguồn hiện có 5 nhóm, 38 chủ đề và 236 ảnh. IMG_9035.JPG được liên kết với hai chủ đề; IMG_8991.JPG vẫn giữ trạng thái unassigned. 38 chủ đề không được tự biến thành 38 hiện vật. Bảng exhibits ban đầu trống, chỉ có dữ liệu sau khi biên tập từ nhãn và tạo bản ghi thật.

| Method | URL | Công dụng |
| --- | --- | --- |
| GET | `/api/v1/groups` | Danh sách nhóm |
| GET | `/api/v1/groups/{id}` | Chi tiết nhóm |
| GET | `/api/v1/topics?group_id=GROUP01&limit=20&offset=0` | Chủ đề, lọc nhóm và phân trang |
| GET | `/api/v1/topics/{id}` | Chi tiết chủ đề |
| GET | `/api/v1/topics/{id}/assets` | Ảnh của chủ đề |
| GET | `/api/v1/assets?classification_status=unassigned` | Danh sách ảnh, lọc trạng thái |
| GET | `/api/v1/assets/{id}` | Metadata và URL ảnh |
| GET | `/api/v1/assets/{id}/file` | File ảnh gốc theo ID |
| GET | `/api/v1/exhibits?topic_id=TOPIC005&q=...` | Hiện vật đã xuất bản |
| GET | `/api/v1/exhibits/{id}` | Chi tiết hiện vật đã xuất bản |
| GET | `/api/v1/qr/resolve?value=museum://topic/TOPIC005` | Phân giải mã QR |
| GET | `/api/v1/admin/exhibits` | Toàn bộ hiện vật gồm bản nháp, cần khóa quản trị |
| POST | `/api/v1/admin/exhibits` | Tạo hiện vật, cần khóa quản trị |
| PATCH | `/api/v1/admin/exhibits/{id}` | Chỉnh sửa hiện vật, cần khóa quản trị |

Các danh sách topics, assets, exhibits trả `{items, total, limit, offset}`, giới hạn 1–100 bản ghi mỗi trang. Topics và exhibits hỗ trợ tìm theo tiêu đề/tên bằng `q`. API danh mục và ảnh dùng cho việc phát triển/đối chiếu, có trường review_status; metadata sơ bộ chưa được xác minh vẫn được trả về. File ảnh được cấp theo ID trong database, không mở toàn bộ thư mục Dataset thành static URL. Ảnh phục vụ hiện tại là bản gốc; có thể bổ sung ảnh tối ưu và Storage sau.

## Biên tập hiện vật và QR

Phiên thiết lập ban đầu đã tạo `.env` gốc với mật khẩu database và khóa quản trị ngẫu nhiên. Giữ file này riêng trên máy. Để đổi khóa, đặt `ADMIN_API_KEY` trong `.env` gốc rồi chạy `docker compose up -d api` để áp dụng. Tạo khóa bằng `openssl rand -hex 32`. Trong Swagger, bấm Authorize và nhập khóa cho header `X-Admin-Key`. Không đóng gói khóa này vào Flutter dành cho khách tham quan. Để trống khóa sẽ vô hiệu hóa admin API (503); sai hoặc thiếu khóa khi đã cấu hình trả 401.

Trong POST `/api/v1/admin/exhibits`, thay các giá trị mẫu bằng thông tin thực đã đối chiếu:

```json
{
  "id": "EX001",
  "topic_id": "TOPIC005",
  "name": "Tên hiện vật theo nhãn",
  "description": "Nội dung đã đối chiếu từ nhãn và nguồn bảo tàng",
  "period": null,
  "material": null,
  "floor": null,
  "room": null,
  "cabinet": null,
  "asset_ids": [],
  "review_status": "needs_review",
  "is_published": false
}
```

Dùng ID thật từ `/assets` để điền asset_ids theo thứ tự hiển thị. Dữ liệu vị trí chưa có bằng chứng để null. Sau khi đối chiếu, PATCH `{"review_status":"verified","is_published":true}` để xuất bản. Public `/exhibits` và QR chỉ trả hiện vật đã xuất bản; bản nháp trả 404. Thay tên, mô tả hoặc vị trí không đổi ID nên giữ nguyên QR. QR nhận `museum://exhibit/EX001`, `museum://topic/TOPIC005` và scheme `museum-demo` tương thích định dạng cũ. Backend không tự nhập EX01–EX03 mẫu của Flutter hoặc checkpoint chưa có dữ liệu khảo sát.

## Chạy Python trực tiếp

Python 3.11 trở lên. PostgreSQL phải được chạy riêng và địa chỉ kết nối phải đúng với máy của bạn. Compose không mở cổng PostgreSQL ra host mặc định; cấu hình cổng phát triển hoặc sử dụng một PostgreSQL có sẵn nếu muốn chạy Python ngoài Docker.

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp -n .env.example .env
alembic upgrade head
python -m scripts.import_dataset
uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
```

`backend/.env` dành cho Python trực tiếp; `.env` ở gốc dành cho Compose. DATABASE_URL có thể ghi đè; khi để trống, backend tạo URL từ POSTGRES_HOST/USER/PASSWORD/DB. CORS_ORIGINS là JSON array các origin web được cho phép, ví dụ `["http://localhost:5173"]`. Flutter iOS/Android không phụ thuộc CORS. Chỉ triển khai khóa quản trị qua HTTPS khi đưa backend ra mạng công khai.

## Kết nối Flutter

Địa chỉ cơ sở là `http://localhost:8002/api/v1` trên iOS Simulator, `http://10.0.2.2:8002/api/v1` trên Android Emulator. iPhone thật cùng mạng Wi-Fi dùng IP LAN của máy chạy API, ví dụ `http://192.168.1.10:8002/api/v1`; localhost trên điện thoại trỏ về chính điện thoại. Với HTTP nội bộ, iOS/Android có thể cần cấu hình quyền mạng/chính sách HTTP riêng cho bản phát triển. URL file_url trả về là đường dẫn từ gốc server, ví dụ `/api/v1/assets/.../file`, phải ghép với origin `http://IP:8002`, không ghép thêm `/api/v1` lần nữa. Khi triển khai dùng HTTPS. Flutter hiện vẫn đang đọc catalog cục bộ; backend này chưa tự chuyển app sang API.

## Migration và kiểm tra

```bash
cd backend
pip install -r requirements-dev.txt
pytest -q
alembic revision --autogenerate -m "describe change"
alembic upgrade head
```

Kiểm thử tự động dùng SQLite tạm để kiểm tra API, migration, import lặp, transaction, SHA-256, bảo vệ file và bản nháp/xuất bản. PostgreSQL là database triển khai; kiểm tra vận hành PostgreSQL bằng Compose khi Docker đang chạy. Không tự tạo bảng khi API khởi động: mọi thay đổi schema đi qua migration.

Tham khảo cấu trúc router từ [FastAPI](https://fastapi.tiangolo.com/tutorial/bigger-applications/), ORM từ [SQLAlchemy](https://docs.sqlalchemy.org/en/20/orm/quickstart.html), và thứ tự khởi động từ [Docker Compose](https://docs.docker.com/compose/how-tos/startup-order/).
