# Embedding và reranking DUT AI

Luồng này chỉ truy xuất tư liệu đã xác minh, chưa tích hợp vào API chat/Gemini.
Không cần cài thêm thư viện Python. Giữ phương pháp từ khóa làm baseline.

## Cấu hình

Thêm vào .env ở gốc project (không commit khóa thật):

```dotenv
DUT_AI_BASE_URL=https://textembedding.dutai.io.vn
DUT_AI_API_KEY=
```

Client chấp nhận URL gốc hoặc URL kết thúc bằng /v1; tự bỏ /v1 để gọi các endpoint native /embed và /rerank.

Biến môi trường tiến trình ưu tiên hơn .env. File hỗ trợ giá trị đơn giản có dấu
nháy và comment; không mở rộng biến kiểu ${OTHER_KEY}.
Client gửi User-Agent museum-assistant/0.1, timeout 120 giây, không tự retry.
Nội dung tư liệu và câu hỏi sẽ được gửi đến DUT AI.

## Chạy từ thư mục backend

Tạo chỉ mục (không cần chạy lại nếu verified_embeddings.json đang hợp lệ):

```bash
python3 -m scripts.build_embeddings
```

Chỉ khi dữ liệu thay đổi, chủ động tạo lại bằng --force. Chỉ mục cũ được giữ
nguyên nếu gọi API thất bại; dữ liệu mới được ghi qua file tạm.

```bash
python3 -m scripts.build_embeddings --force
python3 -m app.services.rag.vector_retrieval --query "Người Sa Huỳnh chôn người chết theo hình thức gì?"
python3 -m app.services.rag.vector_retrieval --topic TOPIC005 --query "Người cổ Bàu Dũ sinh sống bằng gì?"
python3 -m app.services.rag.vector_retrieval --no-rerank --query "Người Sa Huỳnh chôn người chết theo hình thức gì?"
python3 -m scripts.evaluate_vector_retrieval
python3 -m unittest discover -s tests/rag -v
```

Model embedding theo tài liệu dịch vụ: BAAI/bge-m3, 1024 chiều.
Chỉ mục tương thích file đã tạo bằng đoạn lệnh thử trước đó. Lưu hash toàn file
nguồn và từng đoạn; đổi nội dung hoặc định dạng chunks.json yêu cầu tạo lại.
Không đưa review_chunks.json/catalog_chunks.json vào luồng này.

Đánh giá lưu JSON có timestamp UTC vào Dataset/evaluation, không ghi đè báo cáo
cũ. Một vector câu hỏi được dùng chung cho embedding và reranking.
Mặc định lấy tối đa 20 ứng viên rồi chọn 3 đoạn. Với 5 đoạn, reranker xem cả kho
(trừ khi lọc topic). Hit@1/Hit@3 chỉ tính trên câu có đáp án. Các câu không có
đáp án được hiển thị riêng; chưa có bộ quyết định từ chối trả lời.
Điểm cosine và reranking không phải xác suất câu trả lời đúng.

Các bài test dùng client giả, không gửi mạng hay tiêu thụ hạn mức.

## Tìm kiếm trên toàn bộ OCR (chế độ thử nghiệm)

Chỉ mục riêng review_embeddings.json bao phủ review_chunks.json, không nâng trạng
thái bản nháp lên verified. Kết quả luôn in review_status/ocr_status và ảnh nguồn.

Chạy trong backend:

```bash
python3 -m app.services.rag.ingestion --review
python3 -m scripts.build_embeddings --review
python3 -m app.services.rag.vector_retrieval --review --query "Di chỉ Nam Thổ Sơn"
python3 -m app.services.rag.vector_retrieval --review --topic TOPIC006 --query "Di chỉ Nam Thổ Sơn"
python3 -m scripts.evaluate_vector_retrieval --review
```

Lần triển khai này: 252 đoạn, đủ 38 topic, có văn bản tìm kiếm từ 203/236 ảnh.
33 ảnh còn thiếu văn bản tìm kiếm hoặc chưa có topic được liệt kê trong
Dataset/evaluation/full_dataset_coverage.json. Có đoạn OCR không có nghĩa nội dung
đã đọc đúng; vẫn cần duyệt từng nguồn. Không tự tạo nội dung cho ảnh không đọc được.

Chỉ mục thử nghiệm bị từ chối khi dùng retriever ở chế độ mặc định verified.
Cache .cache.json lưu vector theo hash nội dung; chạy lại sau lỗi sẽ dùng lại batch
đã xong. --force cập nhật chỉ mục nhưng vẫn tái sử dụng cache cho nội dung không đổi.
Nếu dịch vụ thay phiên bản model dù giữ cùng tên, cần xóa cache và tạo lại chỉ mục.

Bộ 10 câu hỏi hiện tại vẫn chủ yếu kiểm tra TOPIC005, không đại diện 38 topic.
Nhãn không có đáp án được lập trên kho nhỏ; cần duyệt lại nhãn khi kho mở rộng.
Báo cáo --review là kiểm tra hồi quy xếp hạng, không đánh giá độ chính xác lịch sử
hay khả năng từ chối trả lời cho toàn bộ kho.
