# Báo cáo nhóm — Lab 8 LogiX-VN

Tối đa 5 trang ngoài phụ lục. Số liệu lấy từ file trong `src/reports/`, không chép tay từ terminal.

## 1. Thông tin nhóm

- Tên nhóm: abcd
- Thành viên: xem `TEAM.md`
- Commit chốt (trùng `report/team/decision_adr.md`): 044eb0b

## 2. Mục tiêu và cách tiếp cận

Bài toán: xử lý claim hoàn phí vận chuyển của LogiX-VN theo bốn kiến trúc có cùng chữ ký `run_claim`, rồi chọn kiến trúc ít tự chủ nhất mà vẫn đạt yêu cầu. Nhóm hiểu ranh giới cốt lõi là **tiền, approval và chống ghi trùng do code và host quyết; model chỉ đọc và soạn chữ**. Chữ trong ticket là dữ liệu người dùng, không phải lệnh; nguồn sự thật là order row và policy hiện hành.

Chia việc theo checkpoint (chi tiết trong `TEAM.md`):

- CP1–CP2 (Dư Văn Hùng): cài đặt, đọc contract, viết ba shape workflow, single, orchestrator; nối `crash_at` và handoff phục vụ CP3.
- CP3 (Chu Nguyễn Tùng Dương): test hồi quy cho durability (crash/resume, amount conflict) và handoff (allowlist, tool chỉ đọc, trace/stdout không lộ parent context).
- CP4 (Nguyễn Hữu Mạnh): chạy crash suite, rà approval và ranh giới dữ liệu, ghi `src/reports/crash.json`.
- CP5 (Phan Nguyễn Phan Anh): benchmark 4 shape × 14 claim × 5 seed, test đánh giá công bằng, phân tích chọn shape.

Thứ tự làm: workflow trước (đơn giản nhất, làm chuẩn để so), rồi single (thêm vòng ReAct nhưng giữ quyết định tiền ở code), rồi orchestrator (thêm handoff và investigator). Swarm là bản tham chiếu có sẵn, dùng để đối chứng cost và variance.

## 3. Giải pháp

Cả ba shape dùng chung một khung: đọc claim qua `get_claim_view` (không `SELECT *`), đọc order qua `lookup_order` (chỉ field allowlist, kiểm principal sở hữu đơn), tính quote bằng `compute_compensation`, gọi `durability.issue_refund` với **quote đầy đủ** (host tự trừ phần đơn đã hoàn — T13, T14), và trả kết quả qua `common.finish()` để `refund_effects`, `committed_audit_count` và trace luôn đúng contract.

| Shape | Đọc gì | Ai quyết định | Gọi host |
| --- | --- | --- | --- |
| A `workflow` | claim view → order → quote, theo thứ tự cố định | Code ở mọi bước. MockLLM gọi 1 lần cuối để soạn câu trả lời, chỉ nhận `status` | Shape gọi `issue_refund` nếu quote > 0 |
| B `single` | Vòng `run_react` tối đa 8 bước; model chọn `lookup_order` → `lookup_refund_history` → `compute_compensation` | Model chỉ chọn tool đọc; số tiền lấy từ kết quả tool, không từ chữ của model. Số ngày trễ trong ticket bị bỏ qua | Sau vòng lặp, code của shape gọi `issue_refund` |
| C `orchestrator` | Orchestrator đọc claim view; investigator chạy `lookup_order`, `lookup_policy`, `lookup_refund_history` | Investigator chỉ có tool đọc; orchestrator tự tính quote trên order view của investigator | Orchestrator gọi `issue_refund` |

Nhánh kết quả giống nhau ở cả ba shape: thiếu `order_id` → `needs_info`; không thấy đơn hoặc không sở hữu → `escalated`; quote = 0 → `denied`, không gọi host; quote > 0 mà host từ chối (approval hỏng, approval của claim khác, đơn đã hoàn đủ) → `denied` với `proposal_amount` là quote đầy đủ và host ghi audit `policy_denied`; amount conflict → `failed`; host chấp nhận → `resolved`.

Durability: shape truyền `crash_at` vào `issue_refund` và không bắt `InjectedCrash` (chỉ ghi trace rồi ném tiếp). Dòng ledger và audit `refund_committed` được host ghi trong cùng một transaction với khóa `refund:{claim_id}`, nên chạy lại hay resume sau crash vẫn chỉ có một refund.

Handoff (orchestrator): dựng bằng `lab8.handoff.make_handoff` với `facts={}` và ba tool chỉ đọc; hàm `sanitize` loại field ngoài allowlist, từ chối canary, `parent_secret`, `raw_headers` và mọi tool ghi. Trace ghi handoff đã sanitize, không ghi parent context hay ticket. Một bản tóm tắt bằng LLM không được dùng thay cho allowlist.

Trace: các event `claim`, `order` (field allowlist), `quote`, `handoff`/`investigator` (orchestrator), `react` (single), `host`, `crash`, `decision`. Không ghi ticket, `parent_secret`, header, phone, address, internal_note, item_name; không in ra stdout.

## 4. Kết quả

Bộ public, 14 claim × seed 11,22,33,44,55, MockLLM, cùng bảng giá, một SQLite mới mỗi trial (`src/reports/benchmark.json`):

| Shape | Pass rate | pass^5 | Seed min–max | Variance | Cost/success (VND mô phỏng) | Mean steps | p95 steps | Model calls/trial | Tool calls/trial |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| workflow | 1.000 | 1.000 | 1.000–1.000 | 0.000 | 28.80 | 4.43 | 5 | 1.00 | 2.79 |
| single | 1.000 | 1.000 | 1.000–1.000 | 0.000 | 39.33 | 5.21 | 6 | 4.64 | 3.64 |
| orchestrator | 1.000 | 1.000 | 1.000–1.000 | 0.000 | 57.20 | 4.36 | 5 | 2.00 | 5.57 |
| swarm | 0.986 | 0.929 | 0.929–1.000 | 0.00082 | 49.57 | 2.80 | 3 | 3.00 | 4.66 |

- Swarm fail đúng một trial, `R-swarm-C-002-s55`: ở seed 55 nó tin số ngày trễ trong ticket (5 ngày) thay vì order row (2 ngày) nên trả `resolved` thay vì `denied`. Ba shape nhóm viết đều `denied` đúng ở trial này.
- Crash safety: **20/20** (`src/reports/crash.json`).
- Test: cổng host `python -m pytest -q` → 80 passed; ma trận student `python -m pytest -q -m student -o addopts=` → 248 passed (62/62 mỗi shape).
- Benchmark được chạy lại trên commit `044eb0b`: `by_shape` và toàn bộ 280 trial trùng khớp với file đã commit.
- Tự kiểm trên `student_drop/`: chưa có dữ liệu tại thời điểm viết báo cáo.
- Ablation R1 (workflow so với orchestrator, chỉ đổi topology): pass rate giữ 1.000, cost/success tăng 28.80 → 57.20 (+98.6%) — xem `research_card.md` và `src/reports/ablation_r1.json`.

Quyết định kiến trúc và lý do: xem `report/team/decision_adr.md`. Phiếu nghiên cứu và ablation: xem `report/team/research_card.md`.

## 5. Khó khăn và cách xử lý

- **Shape phải truyền quote đầy đủ.** Nếu shape tự trừ phần đơn đã hoàn rồi mới gửi host thì host trừ thêm lần nữa và T14 fail. Cách xử lý: shape chỉ truyền quote từ `compute_compensation`, để host áp trần theo đơn; `lookup_refund_history` chỉ dùng để đọc.
- **T12 đòi crash phải thật sự xảy ra.** Bọc `issue_refund` trong `try/except` để "an toàn" sẽ nuốt `InjectedCrash` và làm T12 fail. Cách xử lý: chỉ bắt để ghi trace rồi `raise` lại.
- **Môi trường macOS.** Lệnh `python` báo `command not found` khi chưa bật venv; cách xử lý: `python3 -m venv .venv && source .venv/bin/activate` rồi mới cài và chạy (Python 3.12.6 cho kết quả `lab8.smoke pass`, 248 passed).
- **Tác giả commit sai tài khoản.** Commit CP2 `338819a` mang author `tkgame1709` do git config chưa được đặt khi commit. Cách xử lý: đặt `git config user.name/user.email` trong repo trước các commit sau; đóng góp được khai rõ trong `TEAM.md` và báo cáo cá nhân.
- **Tích hợp nhiều nhánh.** CP3, CP4, CP5 làm song song trên nhánh riêng; CP4 phải merge test hồi quy CP3 vào trước khi chạy lại kiểm tra (`7532979`). Sau mỗi lần merge, nhóm chạy lại cổng host và ma trận student để chắc vẫn xanh.

## 6. Tổng hợp đóng góp

Chi tiết đóng góp của từng thành viên nằm trong `TEAM.md` (bảng đóng góp) và báo cáo cá nhân `report/team/MSSV_HoTen.md`.

## 7. Hạn chế và hướng cải thiện

MockLLM không phải model sản xuất; latency là `unavailable`. Ngoài ra:

- MockLLM tất định theo seed nên variance 0 của ba shape nhóm viết chỉ cho thấy model không được quyết định gì; với model thật, single và orchestrator có thể dao động khi model chọn sai tool hoặc dừng sớm.
- Bộ public chỉ 14 claim và pass rate đã chạm trần, nên benchmark phân biệt các shape chủ yếu bằng cost, không bằng chất lượng. Kết quả hidden (40 claim × 5 seed) chưa có.
- Cost là VND mô phỏng theo `config/pricing.yaml`, không phải hóa đơn API.
- Kết luận chọn workflow sẽ đổi nếu claim cần đọc chữ tự do để tìm đơn (không có `order_id` có cấu trúc), hoặc cần tra nhiều nguồn độc lập song song được, hoặc hidden cho thấy workflow fail một nhóm claim mà shape khác qua.
- Hướng cải thiện: thêm claim khó hơn vào bộ tự kiểm (nhiều đơn trong một ticket, approval sát hạn); đo lại khi thay MockLLM bằng model thật nhưng vẫn giữ host chặn ghi tiền.

## 8. Tài liệu tham khảo

- Đề bài và contract của lab: `README.md`, `docs/business_rules.md`, `docs/contracts.md`, `docs/metrics.md`, `docs/architecture.md`.
- Y. Kim, X. Liu và cộng sự, *Towards a Science of Scaling Agent Systems*, arXiv 2512.08296, 2025 — https://arxiv.org/abs/2512.08296
- Google Research Blog, *Towards a science of scaling agent systems: When and why agent systems work*, 28/01/2026 — https://research.google/blog/towards-a-science-of-scaling-agent-systems-when-and-why-agent-systems-work/

## Bổ sung kết quả checkpoint 4

- Host gate: `python -m pytest -q` — **68 passed, 248 deselected**.
- Ma trận public: `python -m pytest -q -m student -o addopts=` — **248 passed, 68 deselected** trên bốn shape; gồm T01–T14 và retry/crash T11–T12.
- Regression CP3: `tests/test_cp3_durability_handoff.py` được tích hợp từ `origin/main`; các kiểm tra crash/resume, amount conflict, handoff allowlist và trace/stdout đều pass trong host gate.
- Crash suite: `python -m lab8.crash_test --count 20 --out reports/crash.json` — **20/20**, không có scenario lỗi. Artifact tại `src/reports/crash.json`.
- Approval và dữ liệu: host tests và ma trận public pass; không có bypass approval hay forbidden secret/PII marker trong các case public. Host giới hạn refund theo approval, số tiền đã thanh toán và entitlement theo đơn; investigator chỉ có tool đọc.
- Giới hạn: chưa có kết quả hidden grading của giảng viên; không kết luận pass rate hoặc leak counts trên hidden pack.
