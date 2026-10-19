# NHẬT KÝ THỰC HIỆN ĐỒ ÁN BIG DATA (LOGBOOK)

## 1. Thông tin thành viên & Tỷ lệ đóng góp (Nhóm 15)

* **Tên đề tài:** Hệ thống Phát hiện Gian lận Thẻ Tín dụng Real Time trên Nền tảng Big Data Lakehouse
* **Học phần:** Dữ liệu lớn (Big Data) - Trường Đại học Công Thương TP. Hồ Chí Minh (HUIT)
* **Khoa:** Công nghệ Thông tin
* **Bảng phân công nhiệm vụ và đóng góp thực tế:**

| STT | Họ và tên | MSSV | Vai trò | Nhiệm vụ chính phụ trách | Đóng góp |
|:---:|:---|:---:|:---:|:---|:---:|
| 1 | **Lê Thanh Phong** | 2001230669 | **Nhóm trưởng** | - Thiết kế tổng thể kiến trúc 5 tầng Medallion Lakehouse.<br>- Xây dựng mô hình Machine Learning (`GBTClassifier`, `RandomForest`, `LogisticRegression`) xử lý mất cân bằng và Point-in-Time Join.<br>- Lập trình Web Dashboard FastAPI (`webapp/backend/main.py`) & giao diện 4 Tab (`index.html`).<br>- Tổng hợp báo cáo, biên soạn tài liệu nghiệm thu và điều phối chung. | **33.4%** |
| 2 | **Nguyễn Thành Phát** | 2001230641 | Thành viên | - Khảo sát bài toán, chuẩn bị tập dữ liệu PaySim / Credit Card Fraud.<br>- Cấu hình hạ tầng phân tán Docker Compose: cụm Hadoop HDFS (NameNode, 3 DataNodes), Zookeeper, Kafka Broker.<br>- Xây dựng Kafka Producer phát sinh luồng dữ liệu thời gian thực (`spark_jobs/ingest/producer.py`) và cơ chế quản lý topic.<br>- Đo kiểm hiệu năng và viết script đồng bộ dữ liệu HDFS (`sync_lakehouse_hdfs.py`). | **33.3%** |
| 3 | **Trần Hưu Đạt** | 2033230060 | Thành viên | - Lập trình động cơ Spark Structured Streaming (`cham_diem.py` & `cap_nhat_trang_thai.py`) với cơ chế Dual-Sink và Watermark 1 phút.<br>- Thiết lập các bảng Delta Lake (Bronze, Silver, Gold) với ràng buộc CHECK và commit log ACID.<br>- Xây dựng 4 DAGs tự động hóa trên Apache Airflow (`gl_giam_sat_streaming`, `gl_kiem_tra_drift`, `gl_huan_luyen_lai`, `gl_bao_tri`).<br>- Thực hiện kiểm thử áp lực Turbo Mode 300 tx/s và benchmark tối ưu hóa Delta Lake. | **33.3%** |

---

## 2. Các mốc thời gian và Tiến độ thực hiện (Milestones)

### Giai đoạn 1: Khảo sát bài toán, Thiết kế kiến trúc & Dựng cụm hạ tầng
* **Mốc 1 (Tuần 1):**
  - Nghiên cứu bài toán phát hiện gian lận thẻ tín dụng trên tập dữ liệu thực tế (hơn 6.3 triệu bản ghi giao dịch).
  - Phân tích 4 thách thức kỹ thuật cốt lõi: Sub-second latency, Extreme class imbalance (tỷ lệ gian lận 0.17%), Concept & Data Drift, Point-in-Time Join.
  - Thiết kế kiến trúc phân tầng Medallion Lakehouse (Bronze - Silver - Gold) kết hợp Kafka và Spark Streaming.
* **Mốc 2 (Tuần 2):**
  - Cấu hình cụm phân tán bằng Docker Compose: Hadoop HDFS 3.3.x (1 NameNode + 3 DataNodes), Confluent Kafka 3.6, Zookeeper.
  - Viết bộ sinh giao dịch trực tuyến đa chế độ (Default, Turbo Mode 300 tx/s, Drift Mode).
  - Khởi tạo topic Kafka `transactions` và luồng Spark Streaming nạp dữ liệu thô vào tầng Bronze dạng Append-Only.

### Giai đoạn 2: Xử lý dữ liệu phân tầng, Huấn luyện Machine Learning & Airflow MLOps
* **Mốc 3 (Tuần 3):**
  - Xây dựng tầng Silver: làm sạch dữ liệu, xử lý trùng lặp, ràng buộc CHECK (`so_tien > 0`), thực hiện Delta MERGE INTO theo mã tài khoản.
  - Hiện thực hóa cơ chế chống rò rỉ dữ liệu Point-in-Time Join với cửa sổ trượt quá khứ `rangeBetween(-3600, -1)`.
  - Huấn luyện và đóng gói pipeline mô hình Machine Learning: GBTClassifier kết hợp trọng số lớp (`weightCol`), đạt Precision@200 = 91.5%, PR-AUC = 0.8870, ROC-AUC = 0.9420.
  - Tích hợp kiểm định thống kê trôi dạt dữ liệu: chỉ số PSI (Population Stability Index) và kiểm định Kolmogorov-Smirnov (KS-test).
* **Mốc 4 (Tuần 4):**
  - Xây dựng 4 DAGs Apache Airflow điều phối tự động: giám sát streaming mỗi 5 phút, kiểm tra drift mỗi 60 phút, tái huấn luyện khi đủ >= 500 nhãn mới, bảo trì Delta Lake Z-ORDER / VACUUM định kỳ.
  - Phát triển ứng dụng Web FastAPI Backend kết hợp giao diện HTML/Tailwind CSS trực quan gồm 4 Tab nghiệp vụ.
  - Tích hợp vòng lặp phản hồi thẩm định Human-In-The-Loop với phím tắt hỗ trợ chuyên viên ngân hàng.

### Giai đoạn 3: Kiểm thử áp lực, Đo lường SLA, Khắc phục sự cố & Hoàn thiện hồ sơ
* **Mốc 5 (Tuần 5):**
  - Thực nghiệm áp lực cao (Turbo Mode Stress Test): 300 giao dịch/giây, 15% gói tin lệch thứ tự out-of-order, 2% bản ghi lỗi.
  - Đo lường độ trễ toàn trình End-to-End: P50 = 42ms, P95 = 88ms, P99 = 120ms (vượt xa cam kết SLA < 2,000ms).
  - Thực thi bộ kiểm thử nghiệm thu tự động kiểm chứng 8 tiêu chuẩn chấp nhận hệ thống (AC1 đến AC8 đều ĐẠT).
  - Xuất báo cáo chính thức (Word & PDF 27 trang chuẩn trường HUIT), hoàn thiện README, nhật ký logbook và đẩy toàn bộ mã nguồn lên GitHub.

---

## 3. Các lỗi kỹ thuật thực tế gặp phải và Biện pháp khắc phục triệt để

Trong quá trình nghiên cứu và triển khai dự án, nhóm đã đối mặt và giải quyết 4 sự cố kỹ thuật phức tạp:

1. **Sự cố xung đột luồng và Crash Python Worker khi ghi vi mô vào Delta Lake trên Windows:**
   * **Hiện tượng:** Khi luồng Spark Streaming hoặc tiến trình ghi nhãn thẩm định thực thi ghi các micro-batches nhỏ vào Delta Lake, Python worker thường xuyên bị đóng băng (crash) do xung đột cơ chế I/O tệp cục bộ trên Windows.
   * **Nguyên nhân:** PySpark JVM socket IPC trên Windows gặp độ trễ lớn khi mở và đóng tệp commit JSON liên tục ở tần suất cao.
   * **Giải pháp khắc phục:** Sử dụng thư viện Rust native `deltalake` (delta-rs engine) cho các tác vụ ghi nhãn phản hồi và đọc snapshot nhanh trong backend FastAPI. Tác vụ ghi diễn ra trực tiếp ở cấp mã máy, triệt tiêu hoàn toàn hiện tượng crash và giảm độ trễ ghi nhãn xuống dưới 50ms.

2. **Sự cố ngoại lệ Empty Collection trong bộ đánh giá Spark MLlib Evaluator:**
   * **Hiện tượng:** Khi chạy đánh giá mô hình MLlib trên các tập dữ liệu vi mô kiểm thử ngẫu nhiên không chứa mẫu gian lận nào (toàn bộ nhãn 0.0), `BinaryClassificationEvaluator` phát sinh ngoại lệ `UnsupportedOperationException: empty collection`.
   * **Nguyên nhân:** Thuật toán tính PR-AUC và ROC-AUC đòi hỏi tập dữ liệu phải tồn tại đồng thời cả 2 lớp nhãn (0 và 1) để xác định ngưỡng phân loại.
   * **Giải pháp khắc phục:** Bổ sung khối kiểm tra phòng vệ `distinct().count() >= 2` trước khi gọi evaluator. Nếu chỉ có 1 lớp nhãn, hệ thống trả về giá trị ước lượng an toàn và ghi log cảnh báo thay vì làm dừng đột ngột luồng xử lý.

3. **Sự cố Undersampling rỗng mẫu gian lận:**
   * **Hiện tượng:** Khi tỷ lệ gian lận trong tập mẫu ban đầu quá thấp hoặc tập lọc tạm thời không có ca gian lận, bước tiền xử lý Undersampling tỷ lệ 1:20 phát sinh lỗi `IllegalArgumentException: DecisionTree requires size of input RDD > 0`.
   * **Nguyên nhân:** Quá trình lọc mẫu gian lận trả về tập rỗng (`count = 0`), khiến RDD đầu vào của cây quyết định không có dữ liệu để phân chia nhánh.
   * **Giải pháp khắc phục:** Bổ sung cơ chế fallback tự động: kiểm tra điều kiện `train_fraud > 0`. Nếu không đủ mẫu, hệ thống tự động nạp bổ sung các mẫu gian lận đã được làm sạch từ tầng Silver để bảo đảm tập huấn luyện luôn có đầy đủ mẫu đại diện.

4. **Sự cố Docker Exec Glob Expansion khi đồng bộ dữ liệu lên HDFS:**
   * **Hiện tượng:** Khi thực thi lệnh `docker exec -i namenode hdfs dfs -put /path/* ...`, ký tự đại diện `*` không được mở rộng trong container mà bị truyền nguyên văn dưới dạng chuỗi ký tự, gây lỗi `No such file or directory`.
   * **Nguyên nhân:** Lệnh gọi trực tiếp qua Docker API không thông qua trình thông dịch shell nên không kích hoạt cơ chế globbing của Linux.
   * **Giải pháp khắc phục:** Bọc toàn bộ câu lệnh đồng bộ qua shell container: `sh -c "hdfs dfs -put /path/* ..."` trong script `scripts/sync_lakehouse_hdfs.py`, đảm bảo đồng bộ thành công 100% dữ liệu Lakehouse và Models lên HDFS NameNode.

---

## 4. Lịch sử Commit tiêu biểu trên GitHub Repository

* **Commit `init`:** Khởi tạo cấu trúc dự án, cấu hình Docker Compose (HDFS, Kafka, Zookeeper) và file `.gitignore` chuẩn.
* **Commit `feat-lakehouse`:** Hiện thực hóa các tầng Delta Lake (Bronze, Silver, Gold), cơ chế CHECK constraint và Delta MERGE INTO.
* **Commit `feat-streaming`:** Lập trình 2 tiến trình Spark Streaming (`cham_diem.py` & `cap_nhat_trang_thai.py`) với Watermark 1 phút và Dual-Sink.
* **Commit `feat-mlops`:** Huấn luyện mô hình GBTClassifier, giải quyết rò rỉ dữ liệu Point-in-Time Join, tích hợp đo lường Precision@200 và kiểm định Concept Drift (PSI & KS-test).
* **Commit `feat-airflow`:** Xây dựng 4 DAGs Airflow tự động hóa điều phối quy trình vận hành và MLOps.
* **Commit `feat-dashboard`:** Phát triển giao diện Web điều hành FraudGuard AI 4 Tab tích hợp bàn làm việc thẩm định Human-In-The-Loop.
* **Commit `test-benchmark`:** Bổ sung kịch bản kiểm thử áp lực Turbo Mode 300 tx/s, benchmark tối ưu hóa Delta Lake OPTIMIZE Z-ORDER và script đồng bộ HDFS.
* **Commit `docs-final`:** Hoàn thiện báo cáo khoa học (Word & PDF), tài liệu kiểm tra HDFS (`HDFS_REPORT.txt`), hướng dẫn cài đặt (`README.md`) và nhật ký thực hiện (`LOGBOOK.md`).