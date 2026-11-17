# Báo cáo cá nhân — Nguyễn Hữu Mạnh

## 1. Thông tin thành viên

- Họ tên: Nguyễn Hữu Mạnh
- MSSV: 2A202604015
- Email: nghmanh04@gmail.com
- GitHub: nghmanh04

## 2. Phần việc phụ trách

- CP4: điều phối việc chạy crash suite, rà soát approval và ranh giới dữ liệu, yêu cầu ghi kết quả vào báo cáo nhóm.
- Phạm vi ghi nhận là công việc có bằng chứng trong phiên hỗ trợ này; bổ sung các phần việc khác nếu có.

## 3. Đóng góp cụ thể

- Phần của thành viên: xác định CP4 là phần cần hoàn thành, rà mã host và các shape liên quan CP4; chạy host gate, ma trận student và crash suite; kiểm tra regression CP3 về crash/resume, handoff và trace/stdout; cập nhật kết quả, giới hạn hidden và artifact vào báo cáo nhóm, kiểm tra và ghi kết quả vào `report/team/group_report.md`, cung cấp thông tin lập báo cáo cá nhân.
- Phần Codex hỗ trợ: 
- Kết quả kiểm tra: host `68 passed`; ma trận student `248 passed`; crash suite `20/20`.
- Chưa ghi nhận code hoặc test mới do thành viên trực tiếp tạo trong phiên này. Không quy các thay đổi triển khai CP2–CP3 trong commit trước cho thành viên nếu chưa có bằng chứng đóng góp riêng.

## 4. Bằng chứng

- `python -m pytest -q` — `68 passed, 248 deselected`.
- `python -m pytest -q -m student -o addopts=` — `248 passed, 68 deselected`.
- `python -m lab8.crash_test --count 20 --out reports/crash.json` — `crash_safety 20/20`.
- Artifact: [`src/reports/crash.json`](../../src/reports/crash.json).
- Báo cáo nhóm: [`group_report.md`](group_report.md).
- Commit CP4 có artifact và báo cáo nhóm: `9d29fc9`.
- Giới hạn: chưa có kết quả grader hidden của giảng viên; không kết luận về hidden pass rate hoặc hidden leak counts.

## 5. Công cụ AI đã dùng

- Công cụ: Codex.
- Cách dùng: đọc contract và code liên quan CP4, chạy các lệnh kiểm tra, xem kết quả JSON và soạn nội dung báo cáo.
- Tự kiểm tra: đối chiếu số pass với output lệnh và `src/reports/crash.json`; ghi rõ hidden pack không có trong repo.

## 6. Tự đánh giá

CP4 có bằng chứng cho host, bốn shape trên ma trận public và 20 điểm crash. Phần đóng góp được ghi nhận ở đây là điều phối và báo cáo; cần bổ sung bằng chứng code/test cá nhân nếu có công việc kỹ thuật khác ngoài phiên này.
