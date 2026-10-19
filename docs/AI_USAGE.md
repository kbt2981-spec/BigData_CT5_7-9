# BẢN KHAI BÁO SỬ DỤNG TRÍ TUỆ NHÂN TẠO (AI USAGE REPORT)

---

## 1. Thông tin chung
* **Đề tài:** Đề tài 2 — Hệ thống phát hiện gian lận giao dịch thẻ theo thời gian thực (Mã đề tài: `bd02_gian_lan`)
* **Sinh viên thực hiện:** Lê Thanh Phong (MSSV: 2001230669)
* **Công cụ AI hỗ trợ:** Google Antigravity / Gemini

---

## 2. Nhật ký & Phạm vi sử dụng AI

| Ngày | Nội dung / Hạng mục | Prompt / Yêu cầu đã dùng | Phần mã do AI khởi tạo / gợi ý | Phần sinh viên đã kiểm tra, tùy biến & sửa đổi |
|---|---|---|---|---|
| **15/10/2026** | Hạ tầng Docker & Airflow | *"Viết cấu hình docker-compose cho Kafka, Spark Standalone, HDFS và Airflow"* | Khung sườn file `docker-compose.yml` | Cấu hình lại các biến môi trường port, mount volume chính xác ổ `D:\Homework\...` trên Windows. |
| **16/10/2026** | Giao diện Web Dashboard | *"Tạo giao diện HTML TailwindCSS và Chart.js theo dõi cảnh báo gian lận và biểu đồ PSI"* | Khung mã HTML/JS `webapp/frontend/index.html` | Tích hợp bảng thẩm định, kết nối các hàm gọi API FastAPI backend và tùy chỉnh style giao diện ngân hàng. |
| **17/10/2026** | Xử lý lỗi JVM Crash & Streaming | *"Tìm nguyên nhân JVM crash khi đọc metadata PipelineModel trên Windows"* | Monkey-patch hàm loadMetadata của DefaultParamsReader | Thử nghiệm, tinh chỉnh bộ nhớ `spark.driver.memory` 4GB và cấu hình Winutils trên Windows. |
| **19/10/2026** | Tinh chỉnh mô hình ML & Chống rò rỉ dữ liệu | *"Xây dựng Time-based split 70/15/15 và so sánh 3 mô hình GBT, Random Forest, Logistic Regression theo chuẩn đề cương"* | Cấu trúc code Time-based split, bộ đánh giá `Precision@200`, `PR-AUC`, `ROC-AUC` | Kiểm tra thứ tự thời gian (`step`), tối ưu tham số tuning mô hình và xác nhận kết quả kiểm toán. |
| **19/10/2026** | Kiểm tra Drift & Airflow DAGs | *"Viết script tính PSI và KS-statistic theo dõi data drift kết hợp BranchPythonOperator"* | Thuật toán tính PSI/KS trong `scripts/tinh_drift.py` và luồng DAG rẽ nhánh | Cấu hình ngưỡng cảnh báo $PSI=0.1$ và retrain $PSI=0.25$, test thực thi trên Airflow. |
| **19/10/2026** | Nâng cấp FastAPI Backend (Mục 2.7, 2.8, A.4) | *"Bổ sung API Health Check giám sát socket port cho 6 dịch vụ cụm, thêm trường oldbalanceOrg/newbalanceOrig, muc_rui_ro, yeu_to_rui_ro vào API canh-bao, thêm API so sánh phiên bản Delta Time Travel"* | Khung code 6 endpoint REST (`/canh-bao`, `/giao-dich/ket-luan`, `/mo-hinh/hieu-nang`, `/ha-tang/trang-thai`, `/kiem-toan/lich-su`, `/kiem-toan/time-travel`, `/kiem-toan/so-sanh-phien-ban`) | Kiểm thử end-to-end tất cả endpoint, tinh chỉnh logic sinh dữ liệu balance PaySim và xác nhận Feedback Loop ghi nhận đúng vào Delta Lake. |
| **19/10/2026** | Nâng cấp giao diện Web Dashboard (Mục 2.7, 2.8, A.4) | *"Nâng cấp UI Dashboard 4 tab: bổ sung bộ lọc đa chiều, bảng đối chiếu số dư PaySim, ma trận nhầm lẫn 4 ô, bảng so sánh 4 thuật toán ML, giám sát hạ tầng live, Version Diff Console Time Travel"* | Giao diện HTML/TailwindCSS/JS hoàn chỉnh cho 4 tab | Tích hợp phím tắt F/L cho thẩm định nhanh, kiểm tra toàn bộ logic auto-select giao dịch tiếp theo, xác nhận biểu đồ PSI Chart và Feature Importance hiển thị đúng dữ liệu thật. |
| **19/10/2026** | Thực nghiệm OPTIMIZE & Z-ORDER (Mục 2.9 & 2.11) | *"Chạy benchmark đo lường hiệu năng trước/sau OPTIMIZE ZORDER BY (tai_khoan_nguon) trên bảng silver.giao_dich"* | Script `scripts/benchmark_optimize.py` đo thời gian truy vấn và thống kê file | Xác nhận kết quả 36.1% tốc độ cải thiện (2.436s → 1.558s), ghi báo cáo `docs/OPTIMIZE_BENCHMARK.md` và tích hợp kết quả vào API `/ha-tang/trang-thai`. |

---

## 3. Cam kết của sinh viên
1. Toàn bộ mã nguồn đã được sinh viên đọc hiểu chi tiết, giải thích được từng dòng lệnh và trực tiếp thử nghiệm chạy thành công trên máy.
2. Mô hình máy học, kiến trúc pipeline và các bảng Delta Lake tuân thủ 100% yêu cầu kỹ thuật của đề cương.
3. Sinh viên chịu hoàn toàn trách nhiệm và sẵn sàng trả lời tất cả các câu hỏi phản biện liên quan đến hệ thống.
