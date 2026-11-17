# Báo cáo cá nhân — Chu Nguyễn Tùng Dương

## 1. Thông tin thành viên

- Họ tên: Chu Nguyễn Tùng Dương
- MSSV: 2A202604016
- Email: tungduong156gli@gmail.com
- GitHub: [ChuTungDuongg](https://github.com/ChuTungDuongg)

## 2. Phần việc phụ trách

Tôi phụ trách CP3 về tính idempotency, khôi phục sau sự cố và bảo mật handoff. Công việc gồm rà soát cách ba shape `workflow`, `single` và `orchestrator` xử lý retry, crash, quyền của investigator và dữ liệu ghi vào trace. Tôi cũng bổ sung test hồi quy và kiểm tra kết quả trên bộ test của lab.

## 3. Đóng góp cụ thể

Trước khi bổ sung test, tôi rà soát các yêu cầu CP3 trong `CHECKPOINTS.md` và đối chiếu với contract, luật nghiệp vụ cùng mã nguồn hiện có. Phần triển khai từ CP2 đã truyền `crash_at` đến host, ném lại `InjectedCrash` sau khi ghi trace, sử dụng ledger của host và tạo handoff với các tool chỉ đọc. Vì các trường hợp kiểm tra chưa chỉ ra lỗi production, tôi giữ nguyên mã của ba shape.

Trong commit [`62a378e`](https://github.com/czx04/K5-L3B-DAY08-abcd-FromWorkflowsToAgents/commit/62a378e18d113da16e440c5da15294015fe834a5), tôi bổ sung `src/tests/test_cp3_durability_handoff.py` với các trường hợp sau:

- Kiểm tra ba điểm crash `before_effect`, `after_effect_before_checkpoint` và `after_checkpoint` trên cả ba shape. Mỗi trường hợp đối chiếu ledger, audit và checkpoint trước và sau khi chạy lại trên cùng SQLite store.
- Kiểm tra chạy lại cùng claim và trường hợp quote thay đổi từ 35.000 xuống 10.000 VND sau khi refund đã commit. Test xác nhận conflict giữ nguyên khoản đã ghi và không tạo thêm audit `refund_committed`.
- Kiểm tra allowlist của handoff, việc từ chối `issue_refund` đối với worker và nội dung handoff thực tế mà orchestrator chuyển cho investigator.
- Đặt các giá trị đánh dấu trong secret, header, ticket và thông tin đơn hàng để kiểm tra chúng không xuất hiện trong handoff, trace, output hoặc kết quả của trường hợp thử.

Các test sử dụng host ledger và SQLite thực tế. Quyết định kỹ thuật là tận dụng cơ chế idempotency của host thay vì tạo cơ chế ghi tiền riêng, đồng thời chỉ sửa production code khi có lỗi được kiểm chứng.

## 4. Bằng chứng

- Commit bổ sung test: [`62a378e18d113da16e440c5da15294015fe834a5`](https://github.com/czx04/K5-L3B-DAY08-abcd-FromWorkflowsToAgents/commit/62a378e18d113da16e440c5da15294015fe834a5). Pull request: [CP3: Durability, Handoff & Crash Recovery Hardening](https://github.com/czx04/K5-L3B-DAY08-abcd-FromWorkflowsToAgents/pull/2).
- `python -m lab8.smoke`: pass.
- `python -m pytest -q`: 68 passed, 248 deselected.
- `python -m pytest -q -m student -o addopts=`: 248 passed, 68 deselected, tương ứng 62 test cho mỗi shape, bao gồm swarm.
- `python -m pytest -q -m student -o addopts= -k "t11 or t12"`: 8 passed, 308 deselected.
- `python -m lab8.crash_test --count 20 --out reports/crash.json`: `crash_safety 20/20`.
- `python -m lab8.demo.buggy_workflow`: in `unsafe refund rows: 2`, minh họa việc chỉ dựa vào checkpoint có thể ghi refund trùng.

Các lệnh được chạy từ `src/` trong môi trường Python riêng cài theo `requirements.txt`. Lần chạy đầu bằng Anaconda gặp lỗi thu thập test do một package `tests` khác che thư mục test của dự án. Môi trường riêng khắc phục xung đột này. Kết quả hidden grader của giảng viên chưa có trong bằng chứng đã kiểm tra.

## 5. Công cụ AI đã dùng

Tôi sử dụng Codex để hỗ trợ rà soát yêu cầu và mã nguồn, bổ sung test, chạy lệnh kiểm tra, phân tích lỗi môi trường và soạn báo cáo. Tôi giao Codex thực hiện các thao tác kỹ thuật trong phạm vi CP3, sau đó đối chiếu nội dung đóng góp với commit, test và output được ghi nhận. Các số liệu trong báo cáo lấy từ kết quả chạy thực tế, không suy ra kết quả hidden.

## 6. Tự đánh giá

Phần CP3 đã có test kiểm tra trực tiếp trạng thái ledger, audit và checkpoint khi retry hoặc khôi phục sau crash. Các test handoff kiểm tra thêm quyền của investigator và dữ liệu xuất hiện trong trường hợp có giá trị đánh dấu. Tôi phân biệt rõ phần triển khai đã có từ CP2 với bộ test bổ sung trong CP3.

Phạm vi kiểm tra chưa bao gồm hidden grader. Ngoài ra, host so sánh số tiền sau khi áp dụng authorization và cap với số đã commit. Test conflict nêu trên chứng minh trường hợp 35.000 xuống 10.000 VND, chưa chứng minh mọi thay đổi quote đều dẫn đến conflict nếu số tiền sau cap không đổi.
