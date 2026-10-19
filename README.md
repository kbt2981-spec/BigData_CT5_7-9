# 🛡️ FraudGuard AI - Real-time Fraud Detection Lakehouse Platform

Hệ thống giám sát và phát hiện gian lận giao dịch tài chính thời gian thực dựa trên kiến trúc **Medallion Delta Lakehouse**, **Hadoop HDFS**, **Apache Kafka**, **PySpark Structured Streaming**, **FastAPI**, và **Apache Airflow**.

* **Đồ án môn học:** Dữ liệu lớn (Big Data)
* **Đơn vị đào tạo:** Khoa Công nghệ Thông tin - Trường Đại học Công Thương TP. Hồ Chí Minh (HUIT)
* **Nhóm thực hiện:** Nhóm 15 (Lê Thanh Phong - 2001230669, Nguyễn Thành Phát - 2001230641, Trần Hưu Đạt - 2033230060)
* **Kho mã nguồn GitHub:** [https://github.com/kbt2981-spec/BigData_CT5_7-9.git](https://github.com/kbt2981-spec/BigData_CT5_7-9.git)

---

## 📌 TỔNG QUAN HỆ THỐNG & KIẾN TRÚC 5 TẦNG

Hệ thống xử lý luồng dữ liệu giao dịch liên tục với độ trễ phản hồi dưới 1 giây (P50 = 42ms, P99 = 120ms) qua 5 tầng công nghệ phân tán:
1. **Tầng Thu nhận (Ingestion Layer):** Bộ phát giao dịch trực tuyến (`spark_jobs/ingest/producer.py`) đẩy luồng dữ liệu JSON vào Apache Kafka topic `transactions` (hỗ trợ mô phỏng độ trễ ngẫu nhiên `<= 30s`).
2. **Tầng Động cơ Xử lý Luồng (Streaming Engine):** Gồm 2 tiến trình Spark Structured Streaming:
   - `cham_diem.py`: Nhận luồng vi mô (trigger 2s), áp dụng mô hình Machine Learning chấm điểm rủi ro và Dual-Sink đồng thời vào tầng Bronze và tầng Gold.
   - `cap_nhat_trang_thai.py`: Duy trì cửa sổ trượt hành vi khách hàng (1h, 24h, 7d) và thực thi Delta MERGE INTO vào tầng Silver.
3. **Tầng Lưu trữ Hồ dữ liệu (Lakehouse Storage Layer):** 5 bảng Delta Lake lưu trữ trên cụm phân tán Hadoop HDFS (1 NameNode + 3 DataNodes):
   - `bronze.giao_dich`: Lưu trữ toàn bộ dữ liệu giao dịch thô dạng Append-Only, ràng buộc `CHECK (so_tien > 0)`.
   - `silver.giao_dich`: Dữ liệu đã làm sạch, chuẩn hóa kiểu timestamp và upsert hồ sơ biến động số dư.
   - `silver.ket_luan_tham_dinh`: Nhãn phản hồi xác nhận gian lận hoặc hợp lệ từ chuyên viên ngân hàng.
   - `gold.diem_rui_ro`: Chứa điểm số rủi ro thời gian thực [0..1] và Top 3 yếu tố giải thích XAI.
   - `gold.theo_doi_drift`: Ghi nhận chỉ số kiểm định phân phối PSI và KS-test định kỳ.
4. **Tầng Điều phối Tự động hóa MLOps (Orchestration Layer):** Apache Airflow điều phối 4 DAGs tự động hóa (`gl_giam_sat_streaming`, `gl_kiem_tra_drift`, `gl_huan_luyen_lai`, `gl_bao_tri`).
5. **Tầng Ứng dụng & Bàn làm việc Thẩm định (Application & Reviewer Layer):** FastAPI Backend (`webapp/backend/main.py`) kết hợp giao diện Web Dashboard 4 Tab (`webapp/frontend/index.html`) tích hợp bàn làm việc thẩm định Human-In-The-Loop.

---

## 🛠️ YÊU CẦU MÔI TRƯỜNG & HẠ TẦNG

* **Hệ điều hành:** Windows 10/11 (64-bit) / Linux Ubuntu 22.04 LTS
* **Java SDK:** OpenJDK 17 (`JDK 17.0.20.1+1`)
* **Hadoop Winutils:** Hadoop 3.3.4 (có `winutils.exe` trong `HADOOP_HOME/bin`)
* **Python:** Python 3.10 hoặc 3.11 (khuyên dùng môi trường ảo `.venv`)
* **Docker & Docker Compose:** Docker Desktop phiên bản mới nhất
* **Apache Kafka Broker:** Confluent Kafka 3.6 (Cổng `localhost:9092`)
* **Apache Spark / PySpark:** 3.5.0
* **Delta Lake:** `delta-spark==3.1.0` / `delta-spark==3.2.0`

---

## ⚙️ HƯỚNG DẪN CÀI ĐẶT TỪNG BƯỚC

### 1. Sao chép Kho mã nguồn (Clone Repository)
```bash
git clone https://github.com/kbt2981-spec/BigData_CT5_7-9.git
cd BigData_CT5_7-9
```

### 2. Khởi tạo Môi trường Ảo Python
```cmd
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt  # hoặc cài đặt: pyspark==3.5.0 delta-spark==3.1.0 fastapi uvicorn pandas pyarrow kafka-python deltalake
```

### 3. Cấu hình Biến môi trường
Khai báo chính xác trong Environment Variables của Windows:
- `JAVA_HOME = D:\Homework\Java\OpenJDK17U-jdk_x64_windows_hotspot_17.0.20.1_1\jdk-17.0.20.1+1`
- `HADOOP_HOME = D:\Homework\Hadoop`
- `PATH = %JAVA_HOME%\bin;%HADOOP_HOME%\bin;%PATH%`

---

## 🚀 QUY TRÌNH VẬN HÀNH HỆ THỐNG

### Cách 1: Khởi động tự động toàn bộ 4 Cửa sổ bằng `run_all.bat`
```cmd
.\run_all.bat
```
Script sẽ tự động khởi động và sắp xếp 4 dịch vụ:
- **Cửa sổ 1:** Web FastAPI Server điều hành (`http://127.0.0.1:8000`)
- **Cửa sổ 2:** Spark Streaming Chấm điểm rủi ro (`cham_diem.py`)
- **Cửa sổ 3:** Spark Stateful Streaming cập nhật trạng thái hồ sơ (`cap_nhat_trang_thai.py`)
- **Cửa sổ 4:** Kafka Producer phát giao dịch trực tuyến (`producer.py`)

### Cách 2: Vận hành thủ công từng phân hệ

#### Bước 1: Khởi động cụm phân tán Docker Compose (HDFS, Kafka, Zookeeper)
```bash
docker compose up -d
docker compose ps
```
Kiểm tra WebHDFS NameNode tại: `http://localhost:9870` (đảm bảo đủ 3 DataNodes).

#### Bước 2: Khởi tạo Topic Kafka
```cmd
python spark_jobs/ingest/create_topic.py
```

#### Bước 3: Huấn luyện Mô hình Machine Learning
```cmd
python spark_jobs/ml/train_model.py
```
*(Mô hình GBTClassifier được huấn luyện và lưu tại `./models/gbt_fraud_model`)*

#### Bước 4: Chạy Luồng Ingestion & Chấm điểm Streaming
```cmd
# Cửa sổ A: Bộ phát giao dịch Kafka
python spark_jobs/ingest/producer.py

# Cửa sổ B: Chấm điểm rủi ro thời gian thực
python spark_jobs/streaming/cham_diem.py

# Cửa sổ C: Cập nhật hồ sơ hành vi trượt
python spark_jobs/streaming/cap_nhat_trang_thai.py
```

#### Bước 5: Khởi chạy Web Dashboard Điều hành
```cmd
python webapp/backend/main.py
```
Mở trình duyệt truy cập: `http://127.0.0.1:8000` để sử dụng đầy đủ 4 Tab giao diện trực quan:
- **Tab 1:** Hàng đợi cảnh báo rủi ro & Bàn làm việc thẩm định Human-In-The-Loop.
- **Tab 2:** Giám sát sức khỏe hạ tầng Live Cluster & Dung lượng 3 tầng Lakehouse.
- **Tab 3:** Ma trận nhầm lẫn ML & Biểu đồ theo dõi Data Drift PSI.
- **Tab 4:** Kiểm toán dữ liệu, Lịch sử Delta Log & Công cụ Time Travel Diff.

---

## 📊 CÁC LỆNH ĐO KIỂM & NGHIỆM THU HỆ THỐNG

1. **Đo lường hiệu năng tối ưu hóa Delta Lake OPTIMIZE Z-ORDER (AC8):**
   ```cmd
   python scripts/benchmark_optimize.py
   ```
   *(Kết quả: Tốc độ truy vấn cải thiện **36.1%**, từ 2.436s xuống 1.558s)*

2. **Kiểm tra giám sát trôi dạt dữ liệu Concept Drift (PSI & KS-test):**
   ```cmd
   python scripts/tinh_drift.py
   ```
   *(Kết quả: PSI = **0.0089** < 0.10, phân phối dữ liệu ổn định)*

3. **Đồng bộ toàn bộ dữ liệu Lakehouse và Models lên HDFS NameNode:**
   ```cmd
   python scripts/sync_lakehouse_hdfs.py
   ```

4. **Kiểm tra trạng thái tập tin trên Hadoop HDFS:**
   ```bash
   docker exec -it namenode hdfs dfs -ls -R /lakehouse
   docker exec -it namenode hdfs dfs -du -h /lakehouse
   ```
   *(Minh chứng chi tiết xem tại `docs/HDFS_REPORT.txt`)*

---

## 📁 HỒ SƠ TÀI LIỆU NỘP BÀI

* 📄 **Báo cáo đồ án (Word):** `docs/BigData_nhom15.docx` (Chuẩn mẫu Trường ĐH Công Thương TP. HCM)
* 📕 **Báo cáo đồ án (PDF):** `docs/BigData_nhom15.pdf` (27 trang chính thức, logo trường, hình ảnh sắc nét)
* 📋 **Nhật ký thực hiện & Đóng góp thành viên:** `LOGBOOK.md`
* 🔍 **Bằng chứng kiểm tra HDFS phân tán:** `docs/HDFS_REPORT.txt`
* 📈 **Báo cáo thực nghiệm tối ưu hóa Delta Lake:** `docs/OPTIMIZE_BENCHMARK.md`
* 🤖 **Bản cam kết sử dụng AI có trách nhiệm:** `docs/AI_USAGE.md`
