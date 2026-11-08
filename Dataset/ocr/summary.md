# Kết quả mở rộng dữ liệu và tìm kiếm bảo tàng

Đã chạy OCR cục bộ trên toàn bộ 236 ảnh; chưa xác minh toàn bộ nội dung lịch sử.

- Tổng số chủ đề: 38.
- 108 ảnh được OCR đánh dấu text_detected; đây không phải chứng nhận nội dung chính xác.
- 128 ảnh được đánh dấu needs_manual_transcription; cần xem ảnh, có thể không có chữ hoặc chữ quá nhỏ/nhiễu.
- 235 tài liệu OCR nháp; ảnh IMG_8798.JPG đã có DOC001/DOC002 nên không tạo thêm tài liệu nháp trùng.
- 252 đoạn trong kho đối chiếu, bao phủ 38 chủ đề. Có thể còn nhiễu, sai dấu và sai thứ tự cột.
- Kho chính giữ 2 tài liệu đã duyệt / 5 đoạn của người dùng.
- IMG_8991.JPG chưa gán chủ đề: giữ trong hàng chờ, không đưa vào tìm kiếm.
- IMG_9035.JPG dùng chung: giữ cả TOPIC030 và TOPIC031.
- 9 kiểm thử pipeline đạt; kiểm tra liên kết và ranh giới bản nháp/đã duyệt đạt.
- Bộ 10 câu cũ chỉ áp dụng TOPIC005: Hit@1=6/7; Hit@3=7/7 trên 7 câu có đáp án. Không phải đánh giá cả 38 chủ đề.

## Tìm kiếm ngay

```bash
cd /home/shin-bkb/code/museum-assistant/backend
python3 -m app.services.rag.retrieval --review
```

Chỉ TOPIC006:

```bash
python3 -m app.services.rag.retrieval --review --topic TOPIC006
```

Bỏ --review để chỉ tìm tài liệu đã duyệt.

## Nơi làm việc tiếp

- Hướng dẫn: `/home/shin-bkb/code/museum-assistant/docs/rag-workflow.md`.
- Checklist từng chủ đề: `/home/shin-bkb/code/museum-assistant/Dataset/review/topics/`.
- Bản JSON chỉnh sửa: `/home/shin-bkb/code/museum-assistant/Dataset/review/documents/`.
- Kết quả OCR thô: `/home/shin-bkb/code/museum-assistant/Dataset/ocr/records/` và `/home/shin-bkb/code/museum-assistant/Dataset/ocr/text/`.

Chỉ đặt verified sau khi kiểm tra với ảnh. Không sửa draft_documents.json trực tiếp vì đó là đầu ra tự động.

## Tình trạng theo chủ đề

- TOPIC001 — Khái quát Bảo tàng Đà Nẵng: 7 ảnh; 3 có văn bản theo bộ lọc OCR; 4 cần kiểm tra thủ công.
- TOPIC002 — Thiên nhiên: 2 ảnh; 0 có văn bản theo bộ lọc OCR; 2 cần kiểm tra thủ công.
- TOPIC003 — Hệ sinh thái biển: 2 ảnh; 1 có văn bản theo bộ lọc OCR; 1 cần kiểm tra thủ công.
- TOPIC004 — Địa chất khoáng sản: 2 ảnh; 1 có văn bản theo bộ lọc OCR; 1 cần kiểm tra thủ công.
- TOPIC005 — Đà Nẵng thời tiền – sơ sử; văn hóa Sa Huỳnh: 16 ảnh; 7 có văn bản theo bộ lọc OCR; 9 cần kiểm tra thủ công.
- TOPIC006 — Đà Nẵng thời kỳ văn hóa Champa: 7 ảnh; 3 có văn bản theo bộ lọc OCR; 4 cần kiểm tra thủ công.
- TOPIC007 — Làng xã: 18 ảnh; 2 có văn bản theo bộ lọc OCR; 16 cần kiểm tra thủ công.
- TOPIC008 — Đà Nẵng – thương cảng sầm uất thời Nguyễn: 9 ảnh; 2 có văn bản theo bộ lọc OCR; 7 cần kiểm tra thủ công.
- TOPIC009 — Đà Nẵng thời phong kiến: 11 ảnh; 4 có văn bản theo bộ lọc OCR; 7 cần kiểm tra thủ công.
- TOPIC010 — Đô thị Đà Nẵng thời thuộc Pháp (1888–1945): 2 ảnh; 2 có văn bản theo bộ lọc OCR; 0 cần kiểm tra thủ công.
- TOPIC011 — Văn hóa xã hội thời thuộc Pháp: 14 ảnh; 1 có văn bản theo bộ lọc OCR; 13 cần kiểm tra thủ công.
- TOPIC012 — Đà Nẵng 1945–1975: đời sống đô thị: 3 ảnh; 3 có văn bản theo bộ lọc OCR; 0 cần kiểm tra thủ công.
- TOPIC013 — Cuộc chiến với liên quân Pháp – Tây Ban Nha (1858–1860): 14 ảnh; 4 có văn bản theo bộ lọc OCR; 10 cần kiểm tra thủ công.
- TOPIC014 — Các phong trào yêu nước tại Đà Nẵng trước 1930: 7 ảnh; 7 có văn bản theo bộ lọc OCR; 0 cần kiểm tra thủ công.
- TOPIC015 — Phong trào cách mạng tại Đà Nẵng 1930–1945: 3 ảnh; 2 có văn bản theo bộ lọc OCR; 1 cần kiểm tra thủ công.
- TOPIC016 — Đà Nẵng trong kháng chiến chống thực dân Pháp (1945–1954): 10 ảnh; 7 có văn bản theo bộ lọc OCR; 3 cần kiểm tra thủ công.
- TOPIC017 — Đà Nẵng trong kháng chiến chống đế quốc Mỹ (1954–1975): 5 ảnh; 3 có văn bản theo bộ lọc OCR; 2 cần kiểm tra thủ công.
- TOPIC018 — Biệt động thành Đà Nẵng: 10 ảnh; 3 có văn bản theo bộ lọc OCR; 7 cần kiểm tra thủ công.
- TOPIC019 — Căn cứ Mõm Nỏ: 2 ảnh; 2 có văn bản theo bộ lọc OCR; 0 cần kiểm tra thủ công.
- TOPIC020 — Khuất Thúc Cự – Chủ tịch Ủy ban kháng chiến huyện Tam Kỳ: 5 ảnh; 2 có văn bản theo bộ lọc OCR; 3 cần kiểm tra thủ công.
- TOPIC021 — Trong cánh cửa lao tù: 18 ảnh; 8 có văn bản theo bộ lọc OCR; 10 cần kiểm tra thủ công.
- TOPIC022 — Chiến công của Mẹ Nhu và bảy dũng sĩ Thanh Khê (26/12/1968): 1 ảnh; 1 có văn bản theo bộ lọc OCR; 0 cần kiểm tra thủ công.
- TOPIC023 — Căn cứ cách mạng K20: 2 ảnh; 2 có văn bản theo bộ lọc OCR; 0 cần kiểm tra thủ công.
- TOPIC024 — 76 ngày đêm sôi sục đấu tranh của Đà Nẵng (1966): 8 ảnh; 4 có văn bản theo bộ lọc OCR; 4 cần kiểm tra thủ công.
- TOPIC025 — Phong trào đấu tranh của học sinh, sinh viên: 3 ảnh; 2 có văn bản theo bộ lọc OCR; 1 cần kiểm tra thủ công.
- TOPIC026 — Đặc khu ủy Quảng Đà: 6 ảnh; 5 có văn bản theo bộ lọc OCR; 1 cần kiểm tra thủ công.
- TOPIC027 — Chiến dịch giải phóng Đà Nẵng (29/3/1975): 5 ảnh; 4 có văn bản theo bộ lọc OCR; 1 cần kiểm tra thủ công.
- TOPIC028 — Chứng tích chiến tranh; Đà Nẵng – kho bom đạn khổng lồ: 6 ảnh; 3 có văn bản theo bộ lọc OCR; 3 cần kiểm tra thủ công.
- TOPIC029 — Chất khai quang và hiểm họa “da cam”; khắc phục hậu quả chiến tranh: 14 ảnh; 8 có văn bản theo bộ lọc OCR; 6 cần kiểm tra thủ công.
- TOPIC030 — Đà Nẵng thời “bao cấp” (1975–1986): 2 ảnh; 2 có văn bản theo bộ lọc OCR; 0 cần kiểm tra thủ công.
- TOPIC031 — Đà Nẵng những năm đầu “đổi mới” (1987–1997): 2 ảnh; 2 có văn bản theo bộ lọc OCR; 0 cần kiểm tra thủ công.
- TOPIC032 — Đà Nẵng tương lai: 2 ảnh; 1 có văn bản theo bộ lọc OCR; 1 cần kiểm tra thủ công.
- TOPIC033 — Văn hóa người Việt xứ Quảng; sinh hoạt cộng đồng làng xã: 6 ảnh; 3 có văn bản theo bộ lọc OCR; 3 cần kiểm tra thủ công.
- TOPIC034 — Văn hóa biển: 4 ảnh; 2 có văn bản theo bộ lọc OCR; 2 cần kiểm tra thủ công.
- TOPIC035 — Nghề nông truyền thống: 2 ảnh; 1 có văn bản theo bộ lọc OCR; 1 cần kiểm tra thủ công.
- TOPIC036 — Nghề thủ công truyền thống: 2 ảnh; 0 có văn bản theo bộ lọc OCR; 2 cần kiểm tra thủ công.
- TOPIC037 — Nghệ thuật trình diễn: 3 ảnh; 1 có văn bản theo bộ lọc OCR; 2 cần kiểm tra thủ công.
- TOPIC038 — Đèn cổ: 1 ảnh; 1 có văn bản theo bộ lọc OCR; 0 cần kiểm tra thủ công.
