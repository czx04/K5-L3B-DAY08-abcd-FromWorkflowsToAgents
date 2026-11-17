# Báo cáo cá nhân — Phan Nguyễn Phan Anh

## 1. Thông tin thành viên

- Họ tên: Phan Nguyễn Phan Anh
- MSSV: 2A202604004
- Email: pnpa102004@gmail.com
- GitHub: alpha19102004

## 2. Phần việc phụ trách

Phụ trách CP5 — benchmark và kiểm thử đánh giá: tổ chức so sánh bốn shape trên cùng bộ public, bổ sung test phục vụ đánh giá, phân tích pass rate, pass^5, độ ổn định theo seed và chi phí mô phỏng để đề xuất lựa chọn kiến trúc.

Phạm vi đã thực hiện gồm tạo `src/reports/benchmark.json`, bổ sung `src/tests/test_cp5_benchmark.py` và kiểm tra lại smoke, toàn bộ test, crash suite cùng định dạng bài nộp. Phần tự kiểm trên bộ hidden chờ dữ liệu `student_drop/` do giảng viên cấp.

## 3. Đóng góp cụ thể

- Xác định phạm vi công việc CP5 và yêu cầu rà soát repo sau khi nhóm tích hợp CP2–CP4. Thực hiện phần đánh giá với sự hỗ trợ của Codex trong việc đọc code, viết test, chạy lệnh và đối chiếu kết quả.
- Tạo benchmark đủ **4 shape × 14 claim × 5 seed = 280 trial**. Giữ cố định corpus, seed `11,22,33,44,55`, MockLLM, mốc policy `2026-11-15` và bảng giá; mỗi trial dùng một SQLite mới để tránh hưởng kết quả refund từ trial trước.
- Bổ sung **5 test** trong `src/tests/test_cp5_benchmark.py`, gồm ba hàm test, trong đó hàm cuối được tham số hóa cho ba shape của nhóm:
  - `test_public_benchmark_compares_all_shapes_on_the_same_trials`: kiểm tra đủ các tổ hợp shape–claim–seed, run id riêng cho mỗi trial, kết quả theo seed và cost per success có tính cả chi phí trial thất bại. Giữ nguyên lỗi tham chiếu của swarm tại `C-002`, seed `55`.
  - `test_student_shapes_selfcheck_without_labels`: bỏ nhãn `expected` khỏi 14 claim public, chạy ba shape trên năm seed; kiểm tra trace hợp lệ, không có lỗi thực thi hay dấu hiệu rò canary, đồng thời các chỉ số cần nhãn được để `None`.
  - `test_renamed_ids_and_injected_tickets_preserve_decisions`: đổi đồng bộ mã claim, order, principal và approval, bỏ `matrix_id`, chuyển nhãn ra ngoài claim và chèn yêu cầu giả mạo trong ticket. Kiểm tra ba shape vẫn giữ quyết định đúng và không ghi token canary trong ticket vào artifact.
- Phân tích benchmark: workflow, single và orchestrator đều đạt `70/70`, pass^5 bằng `1.0`, seed variance bằng `0`. Workflow có cost per success thấp nhất, **28,80 VND mô phỏng**, nên là phương án đề xuất cho luồng nghiệp vụ hiện tại trên bộ public.
- Xác nhận lỗi duy nhất của swarm là tin số ngày trễ trong ticket tại `C-002`, seed `55`, dẫn đến `resolved` trong khi nhãn yêu cầu `denied`. Đây là điểm yếu tham chiếu đã được đề bài mô tả.
- Chạy kiểm tra tích hợp: toàn bộ suite đạt **321 passed**, smoke pass và crash suite đạt **20/20**. Kết quả crash là bước kiểm tra lại sau CP5; phần triển khai cơ chế durability thuộc các checkpoint trước.
- Rà `lab8.check_submission`: tại lần kiểm tra sau benchmark, phần shapes và artifact đều đạt; còn **9 FAIL, 1 WARN** liên quan ADR, research card, bảng đóng góp chưa điền và thay đổi chưa commit. Đây là trạng thái trước khi bổ sung báo cáo cá nhân và dòng đóng góp trong `TEAM.md`.

## 4. Bằng chứng

- Commit test và benchmark CP5: [`75dcd12`](https://github.com/czx04/K5-L3B-DAY08-abcd-FromWorkflowsToAgents/commit/75dcd12).
- Test mới: [`src/tests/test_cp5_benchmark.py`](../../src/tests/test_cp5_benchmark.py).
- Kết quả benchmark: [`src/reports/benchmark.json`](../../src/reports/benchmark.json).
- Kết quả crash suite: [`src/reports/crash.json`](../../src/reports/crash.json).
- Khai báo đóng góp: [`TEAM.md`](../../TEAM.md).

Số liệu dưới đây lấy từ mục `by_shape` trong `benchmark.json`; pass rate và pass^5 hiển thị theo tỷ lệ, chi phí làm tròn hai chữ số thập phân.

| Shape | Trial pass | Pass rate | Pass^5 | Seed min–max | Seed variance | Cost/success (VND mô phỏng) |
| --- | ---: | ---: | ---: | --- | ---: | ---: |
| workflow | 70/70 | 1,000000 | 1,000000 | 1,000000–1,000000 | 0 | 28,80 |
| single | 70/70 | 1,000000 | 1,000000 | 1,000000–1,000000 | 0 | 39,33 |
| orchestrator | 70/70 | 1,000000 | 1,000000 | 1,000000–1,000000 | 0 | 57,20 |
| swarm | 69/70 | 0,985714 | 0,928571 | 0,928571–1,000000 | 0,000816327 | 49,57 |

Run id dẫn chứng trong mục `trials`:

- `R-workflow-C-001-s11`: trial pass, trạng thái `resolved`.
- `R-swarm-C-002-s55`: trial fail, lý do `status resolved != denied`.

Các lệnh đã chạy trong `src/`, bằng Python của môi trường `.venv`:

| Lệnh | Kết quả ghi nhận |
| --- | --- |
| `python -m lab8.smoke` | `lab8.smoke pass` |
| `python -m pytest -q tests/test_cp5_benchmark.py` | `5 passed` |
| `python -m pytest -q -o addopts=` | `321 passed`; bao gồm cả host và student |
| `python -m lab8.crash_test --count 20 --out reports/crash.json` | `crash_safety 20/20` |

Lệnh sinh benchmark:

```text
python -m lab8.benchmark --shapes workflow,single,orchestrator,swarm --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/benchmark.json
```

## 5. Công cụ AI đã dùng

- Công cụ: Codex.
- Cách dùng: hỗ trợ quét repo, đọc yêu cầu CP5 và định nghĩa metric; tạo test đánh giá; chuẩn bị môi trường, chạy smoke, pytest, crash suite, benchmark và checker; tổng hợp số liệu và soạn báo cáo này.
- Cách kiểm chứng trong phiên làm việc: đối chiếu số test với output pytest, kiểm tra đủ 280 trial cùng năm seed trong JSON, kiểm tra lỗi swarm đúng claim và seed đã biết, đối chiếu crash safety với `crash.json` và xác nhận run id có trong benchmark.
- File JSON được sinh bằng công cụ của lab. Các test mới sử dụng fixture công khai và không thay đổi dữ liệu, cấu hình hay các module thước đo bị cấm sửa.

## 6. Tự đánh giá

Phần công việc CP5 đã cung cấp benchmark có thể chạy lại và các test bổ sung cho tính công bằng của phép so sánh, chế độ không nhãn và khả năng giữ quyết định khi ticket chứa yêu cầu giả mạo.
