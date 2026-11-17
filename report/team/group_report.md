# Báo cáo nhóm — Lab 8 LogiX-VN

Tối đa 5 trang ngoài phụ lục. Số liệu lấy từ file trong `src/reports/`, không chép tay từ terminal.

## 1. Thông tin nhóm

- Tên nhóm:
- Thành viên: xem `TEAM.md`
- Commit chốt (trùng `report/team/decision_adr.md`):

## 2. Mục tiêu và cách tiếp cận

Nhóm hiểu bài toán thế nào, chia việc ra sao, thứ tự làm bốn shape.

...

## 3. Giải pháp

Mô tả ba shape nhóm viết (workflow, single, orchestrator): mỗi shape đọc gì, quyết định gì, gọi host ra sao. Chỉ rõ ranh giới code / model (tham khảo [docs/architecture.md](../../docs/architecture.md)), cách handoff được sanitize và trace ghi những event nào.

...

## 4. Kết quả

Bảng so sánh 4 shape trên bộ public (từ `src/reports/benchmark.json`): pass rate, pass^5, seed min–max, variance, cost/success, mean/p95 steps. Kèm crash safety (`src/reports/crash.json`) và, nếu có, kết quả tự kiểm trên `student_drop/`.

...

Quyết định kiến trúc và lý do: xem `report/team/decision_adr.md`. Phiếu nghiên cứu và ablation: xem `report/team/research_card.md`.

## 5. Khó khăn và cách xử lý

Lỗi gặp phải (kèm lệnh, output hoặc ảnh chụp) và cách nhóm xử lý.

...

## 6. Tổng hợp đóng góp

Chi tiết đóng góp của từng thành viên nằm trong `TEAM.md` (bảng đóng góp) và báo cáo cá nhân `report/team/MSSV_HoTen.md`.

## 7. Hạn chế và hướng cải thiện

MockLLM không phải model sản xuất; latency là `unavailable`. Nêu thêm giới hạn của nhóm và điều kiện làm kết luận thay đổi.

...

## 8. Tài liệu tham khảo

...

## Bổ sung kết quả checkpoint 4

- Host gate: `python -m pytest -q` — **68 passed, 248 deselected**.
- Ma trận public: `python -m pytest -q -m student -o addopts=` — **248 passed, 68 deselected** trên bốn shape; gồm T01–T14 và retry/crash T11–T12.
- Regression CP3: `tests/test_cp3_durability_handoff.py` được tích hợp từ `origin/main`; các kiểm tra crash/resume, amount conflict, handoff allowlist và trace/stdout đều pass trong host gate.
- Crash suite: `python -m lab8.crash_test --count 20 --out reports/crash.json` — **20/20**, không có scenario lỗi. Artifact tại `src/reports/crash.json`.
- Approval và dữ liệu: host tests và ma trận public pass; không có bypass approval hay forbidden secret/PII marker trong các case public. Host giới hạn refund theo approval, số tiền đã thanh toán và entitlement theo đơn; investigator chỉ có tool đọc.
- Giới hạn: chưa có kết quả hidden grading của giảng viên; không kết luận pass rate hoặc leak counts trên hidden pack.
