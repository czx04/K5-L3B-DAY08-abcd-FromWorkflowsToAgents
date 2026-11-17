# Decision record

Điền sau dấu `:` trên cùng dòng, không xóa nhãn. Giảng viên và `python -m lab8.check_submission` (chạy trong `src/`) đọc các dòng này bằng máy. Không đổi tên hay dời file này khỏi `report/team/`.
`Shape chọn` phải là đúng một trong: `workflow`, `single`, `orchestrator`, `swarm`. Đây là shape được chấm cổng hidden.

- Shape chọn: workflow
- Commit hash: 044eb0b (main; code shape không đổi từ 338819a, benchmark chạy lại trên commit này cho kết quả trùng `src/reports/benchmark.json`)
- Run id dẫn chứng: R-workflow-C-002-s55 (denied đúng ở trial swarm fail R-swarm-C-002-s55), R-workflow-C-014-s11 (chỉ hoàn phần chênh), R-workflow-C-013-s11 (đơn đã hoàn → denied) — src/reports/benchmark.json
- Pass rate / pass^5 / seed min-max / variance: workflow 1.000 / 1.000 / 1.000–1.000 / 0.000 (70 trial = 14 claim × seed 11,22,33,44,55); đối chứng swarm 0.986 / 0.929 / 0.929–1.000 / 0.00082
- Cost per success (mô phỏng, VND): workflow 28.80; single 39.33; swarm 49.57; orchestrator 57.20
- Crash safety: 20/20 (src/reports/crash.json); workflow qua T12 (crash after_effect_before_checkpoint rồi resume) và tests/test_cp3_durability_handoff.py
- Secret leak / approval bypass: 0 / 0 trên bộ public (70 trace workflow không có CANARY_SECRET_*; C-007, C-009, C-013 đều denied, ledger không có dòng)

Ví dụ một dòng đã điền: `- Shape chọn: workflow`, `- Crash safety: 20/20 (src/reports/crash.json)`.

## Vì sao shape này

So trên cùng 14 claim public, cùng 5 seed `11,22,33,44,55`, cùng MockLLM, cùng bảng giá và mỗi trial một SQLite mới (`controlled_variables` trong `src/reports/benchmark.json`), ba shape nhóm viết đều đạt pass rate 1.000, pass^5 1.000, variance 0. Khi chất lượng ngang nhau thì chọn shape ít tự chủ nhất và rẻ nhất. Workflow có cost/success thấp nhất (28.80 VND mô phỏng, so với 39.33 của single và 57.20 của orchestrator), ít lời gọi model nhất (1 lời gọi/trial, chỉ để soạn câu trả lời) và không có chỗ nào để model chen vào quyết định tiền: quote luôn do `compute_compensation` tính trên order row, còn approval, trần theo đơn và idempotency do host giữ.

## Có đáng đổi lấy multi-agent không

Không, với dữ liệu hiện có. Multi-agent không tăng pass rate (đã chạm trần 1.000) mà làm cost/success gần gấp đôi: orchestrator 57.20 so với workflow 28.80 (ablation R1 trong `research_card.md`). Swarm còn kém hơn: pass^5 0.929 vì ở seed 55 nó tin số ngày trễ ghi trong ticket (C-002: ticket ghi 5 ngày, order ghi 2 ngày) và trả `resolved` thay vì `denied`. Quy trình claim là tuần tự (claim → order → policy → quote → host), không có phần việc độc lập để chia cho nhiều agent chạy song song.

Quyết định sẽ đảo lại nếu: (1) claim không còn `order_id` và dữ liệu có cấu trúc, phải để model đọc chữ tự do để tìm đơn — khi đó single agent có lý do tồn tại; (2) một claim phải tra nhiều nguồn độc lập (nhiều đơn, nhiều hãng vận chuyển, chứng từ hỏng hàng) chạy song song được — khi đó orchestrator + investigator có thể đáng phần cost; (3) bộ hidden cho thấy workflow fail một nhóm claim mà shape khác qua, với chênh pass rate lớn hơn phần cost tăng thêm.

## Trace và bằng chứng

Trace của workflow (`src/traces/<run_id>.json`, ghi bằng `lab8.trace.Trace`) có các event: `claim` (claim_id, có order_id hay không); `order` (chỉ field allowlist của `lookup_order`: order_id, status, delay_days, shipping_fee_vnd, paid_vnd, damage_verified, carrier) hoặc `{visible: false, reason}`; `quote` (amount, reason, clause_ids, parts); `host` (ok, reason trả về từ `issue_refund`); `crash` (điểm crash, nếu có); `decision` (status, proposal_amount, reason). Mọi nhánh return đi qua `common.finish()` nên luôn có trace; khi crash, trace được ghi trước khi ném tiếp `InjectedCrash`.

Cố ý **không** ghi: `parent_secret` và `raw_headers_json` (chứa canary), nội dung ticket (dữ liệu người dùng, có thể chứa lệnh giả mạo hoặc PII), và các cột order ngoài allowlist: phone, address, internal_note, item_name. Shape không đọc claim/order bằng `SELECT *` mà qua `get_claim_view` và `lookup_order`, nên các field này không bao giờ nằm trong bộ nhớ của shape để có thể lọt ra trace. Shape không in gì ra stdout. Trace nằm trong `traces/`, đúng chỗ scanner của grader quét (`trace_path` và mọi file `<run_id>*` cùng thư mục). Nếu trace nằm ngoài chỗ đó thì không thể chứng minh hệ thống sạch, nên grader fail-closed (`missing_trace`); nhóm không ghi log ở nơi nào khác.

## Giới hạn

MockLLM không phải model sản xuất: nó tất định theo seed, nên variance 0 của ba shape nhóm viết phản ánh việc model không được quyết định gì, không phải độ ổn định của một model thật. Cost là VND mô phỏng theo `config/pricing.yaml`, không phải hóa đơn API. Latency để `unavailable`. Bộ public chỉ có 14 claim; kết quả hidden (40 claim × 5 seed) do giảng viên chạy, nhóm chưa có số. Không sửa JSON trong `src/reports/` cho đủ 0.75.
