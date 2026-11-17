# Research card

File này nằm cố định ở `report/team/research_card.md`; `python -m lab8.check_submission` đọc cột "Nhóm điền" bằng máy.

Phần này nối tiếp phần mini research ở buổi lý thuyết (slide 62–63). Chọn **một** câu R1–R4, điền 6 dòng, rồi biến nó thành **một ablation** chạy được trong lab: giữ nguyên model (MockLLM), tool, seed, corpus và giá, chỉ thay đổi một biến.

| Câu | Nguồn (thư viện tham khảo, slide 68–69) | Câu hỏi gợi ý cho lab |
| --- | --- | --- |
| R1 · Scaling | Google Research 2026, *Towards a Science of Scaling Agent Systems* | Task claims chủ yếu tuần tự hay song song được? Dự đoán thêm investigator sẽ làm pass rate và cost/success thay đổi thế nào. |
| R2 · Failure taxonomy | MAST, NeurIPS 2025, *Why Do Multi-Agent LLM Systems Fail?* | Các trial fail của swarm (seed 55) thuộc nhóm nào: lỗi giao việc, lệch mục tiêu, hay lỗi kiểm chứng? |
| R3 · Architecture choices | AgentArch, AACL 2026 | Nếu đổi topology mà giữ nguyên mọi thứ khác, biến nào phải cố định để kết luận còn đúng? |
| R4 · Evaluation confounders | EMNLP 2026, *Rethinking Evaluation of MAS Efficiency* | Làm sao chứng minh chênh lệch giữa A/B/C/D là do topology, không phải do prompt, tool hay seed? |

## Phiếu của nhóm

Điền vào cột cuối. Không xóa hai cột đầu.

| Field | Hướng dẫn | Nhóm điền |
| --- | --- | --- |
| CÂU | R1 / R2 / R3 / R4 | R1 · Scaling |
| SOURCE | Paper/blog, năm, URL, loại bằng chứng (benchmark, production report, blog kinh nghiệm) | Kim, Liu và cộng sự (Google Research, Google DeepMind, MIT), *Towards a Science of Scaling Agent Systems*, arXiv 2512.08296 (12/2025) và blog Google Research 28/01/2026 — https://arxiv.org/abs/2512.08296, https://research.google/blog/towards-a-science-of-scaling-agent-systems-when-and-why-agent-systems-work/. Loại bằng chứng: benchmark có kiểm soát (180 cấu hình agent) |
| CLAIM | Một kết luận gốc của nguồn. Không viết rộng hơn phạm vi paper | Phối hợp nhiều agent giúp nhiều trên task song song hóa được (Finance-Agent: centralized tăng khoảng 81% so với single agent) nhưng làm giảm hiệu năng trên task tuần tự (PlanCraft: mọi biến thể multi-agent giảm 39–70%); với task nhiều tool, chi phí phối hợp tăng nhanh hơn số tool |
| BOUNDARY | Model / dataset / setup giới hạn kết luận đó | Model thật thuộc ba họ OpenAI GPT, Google Gemini, Anthropic Claude; 4 benchmark Finance-Agent, BrowseComp-Plus, PlanCraft, Workbench; 5 kiến trúc (single, independent, centralized, decentralized, hybrid) với ngân sách token cân bằng. Không có MockLLM tất định, không có host chặn ghi tiền như lab này |
| HYPOTHESIS | Nếu đổi shape A→B (hoặc bật/tắt một thành phần), metric X sẽ đổi theo hướng nào, khoảng bao nhiêu | Claim LogiX là task tuần tự (claim → order → policy → quote → host). Đổi workflow (A) sang orchestrator (C), tức thêm một lớp investigator, sẽ không tăng pass rate (đã ở 1.000) và làm cost/success tăng khoảng 50–100% do thêm lời gọi model và tool |
| METHOD | Biến giữ cố định: model, tools, seed, corpus, giá, evaluator. Biến duy nhất được thay đổi: … | Giữ cố định: MockLLM, bộ tool đọc trong `lab8.tools`, seed 11,22,33,44,55, corpus `data/public_claims.jsonl` (14 claim), `config/pricing.yaml`, host `durability.issue_refund`, evaluator `lab8.metrics`, một SQLite mới mỗi trial. Biến duy nhất được thay đổi: topology — workflow (không có investigator) so với orchestrator (orchestrator + investigator chỉ đọc qua handoff) |
| FAILURE / METRIC | Một lỗi dự kiến và cách đo nó: pass rate, pass^5, variance, cost/success, leak, bypass | Lỗi dự kiến: overhead phối hợp — thêm agent làm tăng chi phí mà không tăng chất lượng; đo bằng cost/success và mean tool/model calls với pass rate, pass^5 giữ nguyên. Kiểm thêm leak (CANARY trong trace) để chắc handoff không làm lộ secret |

## Kết quả ablation

- Lệnh đã chạy (copy nguyên văn): `python -m lab8.benchmark --shapes workflow,orchestrator --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/ablation_r1.json`
- Run id / file report: `src/reports/ablation_r1.json` (140 trial, run id dạng `R-workflow-C-001-s11` … `R-orchestrator-C-014-s55`); số trùng với `src/reports/benchmark.json`
- Kết quả so với hypothesis (đúng / sai / không kết luận được), kèm số liệu: Đúng hướng. Pass rate và pass^5 không đổi (workflow 1.000 / 1.000; orchestrator 1.000 / 1.000; variance 0 cả hai). Cost/success tăng từ 28.80 lên 57.20 VND mô phỏng (+98.6%, sát cận trên của khoảng dự đoán) vì mean tool calls tăng từ 2.79 lên 5.57 và model calls từ 1 lên 2 mỗi trial; mean steps gần như bằng nhau (4.43 so với 4.36). Không có trace nào chứa CANARY_SECRET_*. Vì pass rate đã chạm trần trên bộ public nên ablation này không cho kết luận được về chiều "multi-agent làm giảm chất lượng" như PlanCraft, chỉ khẳng định phần chi phí
- Giới hạn: MockLLM không phải model sản xuất, latency là `unavailable`.

Muốn đi xa hơn một ablation để lấy điểm cộng thì xem [docs/bonus_topics.md](../../docs/bonus_topics.md).
