# RAG dữ liệu bảo tàng — OCR cục bộ và tìm kiếm

## Phạm vi

Ảnh gốc và metadata là nguồn tham chiếu. OCR không tạo ra sự thật lịch sử: chữ nhỏ, nghiêng, phản sáng, nhãn nhiều cột và song ngữ có thể bị nhận sai hoặc sai thứ tự. Không suy đoán hiện vật từ tên ảnh. Không tự đặt trạng thái verified cho OCR.

Hai tài liệu DOC001, DOC002 đã có của người dùng được giữ nguyên. Ghi chú cũ còn nhắc “cần đối chiếu” dù trạng thái là verified: người biên tập nên cập nhật ghi chú cho khớp việc đã kiểm tra; pipeline không tự sửa nội dung đó.

## Các thư mục

- Dataset/curated/documents.json: dữ liệu đã biên tập do người dùng quản lý; lệnh OCR không sửa file này.
- Dataset/ocr/records/: kết quả từng ảnh, SHA-256, cấu hình, chữ nhận dạng và bounding box theo kích thước ocr_size.
- Dataset/ocr/text/: bản chữ OCR thô.
- Dataset/ocr/draft_documents.json: bản nháp tự động; không sửa trực tiếp vì chạy OCR lại có thể tái tạo.
- Dataset/ocr/review_queue.json: mọi ảnh, kể cả ảnh không nhận được chữ, ảnh dùng chung và chưa gán chủ đề.
- Dataset/ocr/report.json: thống kê từng topic và những ảnh cần xử lý thủ công.
- Dataset/review/documents/: bản nháp có thể sửa; export_review không ghi đè file đã tồn tại.
- Dataset/review/topics/: checklist đối chiếu theo chủ đề, chứa đường dẫn nguồn và bản chỉnh sửa.
- Dataset/processed/chunks.json: chỉ tài liệu verified, có gán topic.
- Dataset/processed/review_chunks.json: kho đối chiếu có cả OCR chưa xác minh; không dùng để trả lời khách.
- Dataset/evaluation/questions.json: bộ đánh giá người dùng đã tạo, không bị thay bằng câu hỏi tự sinh.

language=und trong OCR nghĩa là chưa xác định/tách ngôn ngữ, không phải lỗi. Tên tài liệu OCR lấy từ danh mục + tên ảnh, không khẳng định đó là tiêu đề thực trên bảng.

## Thiết lập OCR

Máy hiện có runtime cục bộ tại `.tools/tesseract`, được bỏ qua bởi Git. Runtime này lấy từ các gói Ubuntu bằng dpkg-deb, không thay đổi gói hệ thống. Khi dùng máy khác, cài Tesseract và dữ liệu vie/eng phù hợp hệ điều hành; script cũng nhận tesseract từ PATH. Python cần Pillow (backend/requirements-ocr.txt). Không cần API key hoặc gửi ảnh đến dịch vụ bên ngoài.

## Chạy lại OCR

Từ thư mục gốc project:

```bash
python3 backend/scripts/ocr_dataset.py --workers 2
```

Mặc định tái sử dụng kết quả khi checksum ảnh và cấu hình khớp. Chỉ dùng --force khi cần OCR lại. Hai worker và một luồng Tesseract mỗi worker giúp giảm áp lực RAM. Text_detected chỉ là gợi ý có chữ, không phải chứng nhận đúng. needs_manual_transcription có thể do ảnh không có chữ, nhiễu hoặc nhãn nhỏ.

## Tạo chỉ mục và tìm kiếm

```bash
cd backend
python3 -m app.services.rag.ingestion
python3 -m app.services.rag.ingestion --review
python3 -m app.services.rag.retrieval
python3 -m app.services.rag.retrieval --review
python3 -m app.services.rag.retrieval --review --topic TOPIC006
python3 -m app.services.rag.retrieval --review --query "Nam Thổ Sơn" --top-k 3
```

Không có --topic: tìm toàn bộ chủ đề có trong kho đang chọn. Không có --review: chỉ tìm kho đã duyệt. Ảnh chưa gán topic không được đưa vào chỉ mục nhưng vẫn có trong queue. Ảnh dùng chung giữ topic_ids và có thể tìm bằng cả hai topic. Chỉ mục review loại các mẩu rất ngắn (dưới 6 chữ cái hoặc dưới 2 từ) và gom dòng OCR thành đoạn; bản gốc vẫn được giữ đầy đủ. Quy tắc này có thể bỏ sót nhãn ngắn, không sửa được thứ tự nhiều cột. Điểm tìm kiếm vẫn là baseline số từ trùng; không phải xác suất câu trả lời đúng. Câu không có đáp án có thể vẫn có kết quả liên quan.

## Biên tập và duyệt một tài liệu

```bash
python3 -m scripts.export_review
```

1. Mở checklist Dataset/review/topics/TOPICxxx.md.
2. Mở ảnh và file JSON chỉnh sửa tương ứng trong Dataset/review/documents/.
3. Sửa title và text theo ảnh. Loại chữ nhiễu, sửa thứ tự đọc và xác minh tên, ngày tháng.
4. Nếu ảnh có nhiều bảng hoặc song ngữ, tạo nhiều tài liệu với document_id riêng; cùng tham chiếu source_asset_ids. Đặt language=vi hoặc en sau khi tách. Không dịch rồi coi là nguyên văn trên ảnh.
5. Giữ exhibit_id=null cho bảng nói chung về chủ đề. Không suy đoán mã hiện vật.
6. Chỉ khi đã đối chiếu đầy đủ: đặt review_status=verified và ghi nhận việc kiểm tra trong review_notes. Nếu chưa đọc rõ, giữ needs_review.
7. Nhập bản đã duyệt:

```bash
python3 -m scripts.import_reviewed ../Dataset/review/documents/TEN_FILE.json
python3 -m app.services.rag.ingestion
python3 -m app.services.rag.ingestion --review
```

Thay TEN_FILE bằng tên thật. Import kiểm tra ID ảnh, tên ảnh, topic, ngôn ngữ, trạng thái và phiên bản; không thể tự kiểm chứng lịch sử. Muốn cập nhật cùng document_id phải tăng version. Nếu một ảnh chỉ được chép một phần, biên tập đầy đủ các phần còn lại trước khi coi ảnh đó đã hoàn tất. Chỉ mục review bỏ bản OCR nguyên ảnh khi ảnh đã có tài liệu verified để tránh lặp, không hàm ý toàn bộ ảnh đã được chép đủ.

## Kiểm thử

Từ backend:

```bash
python3 -m unittest discover -s tests/rag -v
python3 -m scripts.evaluate_retrieval
python3 -m scripts.check_knowledge
```

Bộ 10 câu cũ vẫn chỉ đánh giá chủ đề TOPIC005. Không dùng kết quả 6/7 hoặc 7/7 để khẳng định chất lượng cả 38 chủ đề. Khi duyệt thêm chủ đề, bổ sung câu hỏi có đáp án và không có đáp án dựa trên nguồn đã đọc; dành một phần câu hỏi mới làm tập kiểm tra chưa dùng chỉnh thuật toán.

Chưa tích hợp mô hình sinh câu trả lời, embedding, voice hoặc API chat. Đây là nền dữ liệu và tìm kiếm cục bộ.
