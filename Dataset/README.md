# Nguồn dữ liệu Bảo tàng Đà Nẵng

Ảnh khảo sát được phân nhóm theo `danh_muc_bao_tang.md`. Tên ảnh và nội dung ảnh gốc được giữ nguyên. Đây là dữ liệu biên tập sơ bộ để chuẩn bị nhập backend; chưa phải nội dung thuyết minh đã được xác minh.

```text
Dataset/
├── topics/                 # 5 nhóm lớn, 38 thư mục chủ đề có README và ảnh gốc
├── shared/                 # Một bản ảnh được nhiều chủ đề tham chiếu
├── unassigned/             # Ảnh có thật nhưng danh mục chưa chỉ định chủ đề
└── metadata/
    ├── groups.json         # Nhóm chủ đề
    ├── topics.json         # Chủ đề, mô tả và nguồn tham chiếu
    ├── assets.json         # Một bản ghi cho mỗi ảnh; đường dẫn, kích thước, SHA-256
    ├── topic_assets.json   # Quan hệ nhiều-nhiều giữa chủ đề và ảnh
    ├── source_manifest.json # Đường dẫn trước/sau để kiểm tra hoặc khôi phục
    ├── classification_report.json # Chênh lệch số ảnh, khoảng số khuyết, ảnh dùng chung
    └── catalog_source.md   # Bản chụp danh mục dùng khi phân loại
```

## Cách dùng cho database

Nhập theo thứ tự `groups.json` → `topics.json` và `assets.json` → `topic_assets.json`. Trường `group_id`, `topic_id`, `asset_id` dùng để liên kết các bản ghi. Các file JSON là mảng bản ghi UTF-8. Đường dẫn `path` và `directory` đều tính từ thư mục `Dataset/`, dùng dấu `/`, không phụ thuộc đường dẫn máy cá nhân. Sau khi upload ảnh lên Storage, backend lưu thêm storage key hoặc URL tương ứng cho mỗi asset ID; không dùng đường dẫn máy cá nhân làm URL công khai.

Mã TOPIC001 đến TOPIC038 là mã chủ đề do dự án cấp theo thứ tự danh mục, chưa phải mã kiểm kê bảo tàng. Một chủ đề có thể chứa nhiều hiện vật. Cần tạo bản ghi `exhibits` và quan hệ `exhibit_assets` sau khi đọc nhãn để xác định từng hiện vật; không tự coi mỗi ảnh hoặc mỗi chủ đề là một hiện vật.

`review_status = needs_review` và `asset_role = unclassified` thể hiện dữ liệu đang chờ đối chiếu. Chưa suy đoán tầng, phòng, tọa độ, tên hiện vật, vai trò ảnh (nhãn/toàn cảnh/hiện vật) hoặc nội dung OCR từ số thứ tự ảnh. Chỉ bổ sung khi có căn cứ từ ảnh hoặc khảo sát.

## Các điểm cần đối chiếu

- Có 236 ảnh thực tế; danh mục ghi 237 ảnh. Chênh lệch chưa xác định nguyên nhân.
- IMG_8991.JPG có trong nguồn nhưng không được liệt kê ở chủ đề nào; nằm trong `unassigned/`.
- IMG_9035.JPG được cả TOPIC030 và TOPIC031 tham chiếu; lưu một lần trong `shared/`, giữ hai quan hệ trong `topic_assets.json`.
- Các dải ảnh trong danh mục có thể khuyết số. `classification_report.json` ghi các tên không hiện diện trong dải để kiểm tra; không khẳng định ảnh bị mất.
- Ảnh có nội dung giống nhau hoàn toàn (nếu có) vẫn được giữ; xem `identical_content_groups` trong báo cáo.

## Kiểm tra và khôi phục

Từ thư mục dự án chạy `python3 scripts/organize_museum_dataset.py --verify` để đối chiếu đủ ảnh, kích thước, SHA-256 và khóa liên kết. Chạy lại `--apply` khi đã sắp xếp chỉ kiểm tra, không di chuyển lần nữa. `source_manifest.json` lưu tên gốc và vị trí mới của từng ảnh; dùng các cặp đường dẫn đó để đưa ảnh về cấu trúc phẳng khi cần. Nếu dừng giữa quá trình di chuyển, mỗi ảnh phải có ở đường dẫn gốc hoặc đường dẫn mới ghi trong manifest; xử lý phần còn lại dựa trên manifest trước khi chạy lại.

## OCR và RAG cục bộ

Xem [quy trình OCR, duyệt dữ liệu và tìm kiếm](../docs/rag-workflow.md). `ocr/` là bản tự động chưa xác minh; `review/` là bản để đối chiếu; chỉ `curated/` với trạng thái verified được đưa vào chỉ mục trả lời chính thức.
