# Team

## Thông tin nhóm

- Tên nhóm: abcd
- Lớp: L3B
- Repo nhóm: `K5-L3B-DAY08-abcd-FromWorkflowsToAgents` (xem [SUBMISSION.md](SUBMISSION.md))
- URL repo, nhánh nộp, commit chốt: https://github.com/czx04/K5-L3B-DAY08-abcd-FromWorkflowsToAgents, nhánh `main`, commit `044eb0b`

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
|   1 | Dư Văn Hùng | 2A202603975 | dhit2k4@gmail.com | czx04 | CP1–CP2 — ba shape workflow, single, orchestrator; integration |
|   2 | Chu Nguyễn Tùng Dương | 2A202604016 | tungduong156gli@gmail.com | ChuTungDuongg | CP3 — durability, idempotency, handoff |
|   3 | Nguyễn Hữu Mạnh | 2A202604015 | nghmanh04@gmail.com | nghmanh04 | CP4 — crash suite, approval, ranh giới dữ liệu |
|   4 | Phan Nguyễn Phan Anh | 2A202604004 | pnpa102004@gmail.com | alpha19102004 | CP5 — benchmark và kiểm thử đánh giá |

Gợi ý chia vai:

- Nhóm 6 người: integration; workflow; single agent; orchestrator; ledger/policy/crash; eval/report.
- Nhóm 4 người: workflow + integration; single; orchestrator + handoff; ledger + evaluation.

## Bảng đóng góp

`python -m lab8.check_submission` đọc bảng này bằng máy: giữ nguyên tiêu đề `## Bảng đóng góp` và các cột. Mỗi người một dòng: commit có nội dung và ít nhất một test đã thêm hoặc sửa.

| Người | Vai | Commit | Test đã thêm hoặc sửa |
| --- | --- | --- | --- |
| [Dư Văn Hùng — 2A202603975](report/team/2A202603975_DuVanHung.md) | CP1–CP2 — ba shape workflow, single, orchestrator; nối crash_at/handoff cho CP3; có Claude hỗ trợ | [`338819a`](https://github.com/czx04/K5-L3B-DAY08-abcd-FromWorkflowsToAgents/commit/338819a), [`aae64bd`](https://github.com/czx04/K5-L3B-DAY08-abcd-FromWorkflowsToAgents/commit/aae64bd) | `src/tests/test_cp2_shapes.py`: 7 test về claim không tồn tại, tiền do code tính và không đổi theo seed, agent single chỉ đọc và không vượt 8 bước |
| [Chu Nguyễn Tùng Dương — 2A202604016](report/team/2A202604016_ChuNguyenTungDuong.md) | CP3 — durability, idempotency và handoff | [`62a378e`](https://github.com/czx04/K5-L3B-DAY08-abcd-FromWorkflowsToAgents/commit/62a378e) | `src/tests/test_cp3_durability_handoff.py`: 14 test về crash/resume ở 3 điểm crash, amount conflict, allowlist handoff và trace/stdout không lộ parent context |
| [Nguyễn Hữu Mạnh — 2A202604015](report/team/2A202604015_NguyenHuuManh.md) | CP4 — crash suite, rà approval và ranh giới dữ liệu | [`9d29fc9`](https://github.com/czx04/K5-L3B-DAY08-abcd-FromWorkflowsToAgents/commit/9d29fc9) | Chưa có — cần bổ sung |
| [Phan Nguyễn Phan Anh — 2A202604004](report/team/2A202604004_PhanNguyenPhanAnh.md) | CP5 — benchmark, test đánh giá và phân tích lựa chọn shape; có Codex hỗ trợ | [`75dcd12`](https://github.com/czx04/K5-L3B-DAY08-abcd-FromWorkflowsToAgents/commit/75dcd12) | `src/tests/test_cp5_benchmark.py`: 5 test về so sánh công bằng, claim không nhãn, đổi mã và ticket giả mạo |

## Cá nhân

Mỗi thành viên đồng thời tạo một báo cáo riêng trong `report/` theo dạng:

```text
report/team/MSSV_HoTen.md
```

Ví dụ: `report/team/20241234_NguyenVanAn.md`.

Sao chép mục dưới đây cho từng thành viên.

## MSSV_HoTen

### Phần việc phụ trách

-

### Đóng góp cụ thể

-

### Bằng chứng

-
