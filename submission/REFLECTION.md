# Reflection — Lab 19

**Tên:** Phan Quốc Anh
**Cohort:** whopqa/2A202600890_PhanQuocAnh_Day19
**Path đã chạy:** lite

---

## Câu hỏi (≤ 200 chữ)

- **exact**: BM25 (96.7%) và Hybrid (96.7%) thắng nhờ so khớp từ khóa verbatim chính xác.
- **paraphrase**: BM25 (33.3%) và Hybrid (32.0%) vượt trội Vector (24.0%) vì mô hình `bge-small-en-v1.5` tối ưu hóa kém trên ngữ nghĩa tiếng Việt. Production nên đổi sang `bge-m3`.
- **mixed**: Hybrid thắng tuyệt đối (100.0%) nhờ dung hợp cả từ khóa chính xác và ngữ cảnh ngữ nghĩa.
- **Không dùng hybrid khi**: Hệ thống tìm kiếm mã hàng, số serial, tag cố định (cần BM25/SQL thuần túy); hoặc khi hạ tầng cực kỳ giới hạn về tài nguyên/độ trễ (hybrid tăng P99 latency từ 11.6ms lên 18.3ms).

---

## Điều ngạc nhiên nhất khi làm lab này

Sự khác biệt rõ rệt về hiệu năng tìm kiếm paraphrase tiếng Việt khi dùng mô hình embedding chỉ hỗ trợ tốt tiếng Anh, và tầm quan trọng của việc chọn đúng embedding model trong sản xuất.

---

## Bonus challenge

- [x] Đã làm bonus (xem `bonus/`)
- [ ] Pair work với: _Không có_
