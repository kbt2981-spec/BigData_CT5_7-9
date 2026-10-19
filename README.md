# 🛡️ FraudGuard AI - Real-time Fraud Detection Lakehouse Platform

Hệ thống giám sát và phát hiện gian lận giao dịch tài chính thời gian thực dựa trên kiến trúc **Medallion Delta Lakehouse**, **Apache Kafka**, **PySpark Structured Streaming**, **FastAPI**, và **Apache Airflow**.

---

## 📌 TỔNG QUAN HỆ THỐNG & KIẾN TRÚC

Hệ thống xử lý luồng dữ liệu giao dịch liên tục với độ trễ phản hồi dưới 2 giây qua 3 tầng Medallion Lakehouse:
1. **Bronze Layer (Raw Data Lake):** Tiếp nhận dữ liệu thô dạng JSON từ Kafka topic `transactions` và lưu vào Delta Table dạng Append-Only qua `consumer_bronze.py`.
2. **Silver Layer (Cleaned Data):** Giải mã JSON, làm sạch dữ liệu bằng `process_silver.py`, lọc bỏ NULL/trùng lặp, chuẩn hóa kiểu dữ liệu timestamp.
3. **Gold Layer (Analytics & Scoring):**
   - **Batch Aggregation:** Thống kê chỉ số kinh doanh thông qua `process_gold.py`.
   - **Real-time Scoring:** Nạp mô hình `GBTClassifier` được huấn luyện từ `train_model.py` thông qua luồng `cham_diem.py` để chấm điểm rủi ro gian lận thời gian thực.
4. **API & Dashboard:** FastAPI Backend (`main.py`) đọc trực tiếp bảng Gold/Parquet cung cấp RESTful APIs cho Web Dashboard giao diện `index.html`.

---

## 🛠️ YÊU CẦU MÔI TRƯỜNG & THƯ VIỆN

* **Hệ điều hành:** Windows 10/11 (64-bit)
* **Java:** OpenJDK 17 (`JDK 17.0.20.1+1`)
* **Hadoop Winutils:** Hadoop 3.3.4 (Yêu cầu có `winutils.exe` trong `HADOOP_HOME/bin`)
* **Python:** Python 3.10+
* **Apache Kafka:** Local Server (`localhost:9092`)
* **Apache Spark / PySpark:** 3.5.0
* **Delta Lake:** `delta-spark` 3.1.0 / 3.2.0

---

## ⚙️ HƯỚNG DẪN CÀI ĐẶT

### 1. Khởi tạo Môi trường Ảo (Virtual Environment)
```cmd
python -m venv .venv
.venv\Scripts\activate
```

### 2. Cài đặt các Thư viện Python
```cmd
pip install pyspark==3.5.0 delta-spark==3.1.0 fastapi uvicorn pandas pyarrow kafka-python chart.js
```

### 3. Cấu hình Môi trường Cục bộ (Windows)
Đảm bảo các đường dẫn Java và Hadoop được khai báo chính xác trong biến môi trường hệ thống:
- `JAVA_HOME = D:\Homework\Java\OpenJDK17U-jdk_x64_windows_hotspot_17.0.20.1_1\jdk-17.0.20.1+1`
- `HADOOP_HOME = D:\Homework\Hadoop`

---

## 🚀 QUY TRÌNH VẬN HÀNH HỆ THỐNG (STEP-BY-STEP)

### Bước 1: Khởi động Apache Kafka
Mở cửa sổ dòng lệnh riêng để bật Kafka Broker:
```cmd
bin\windows\kafka-server-start.bat config\server.properties
```

### Bước 2: Huấn luyện Mô hình Machine Learning (train_model.py)
Thực hiện 1 lần đầu tiên để khởi tạo tệp mô hình tại `./models/gbt_fraud_model`:
```cmd
python spark_jobs/ml/train_model.py
```

### Bước 3: Khởi chạy Luồng Ingestion (Kafka Producer & Consumer Bronze)
1. Bật **Kafka Producer**:
   ```cmd
   python spark_jobs/ingest/producer_kafka.py
   ```
2. Bật **Consumer Bronze**:
   ```cmd
   python spark_jobs/ingest/consumer_bronze.py
   ```

### Bước 4: Chạy ETL Tầng Silver & Gold
```cmd
# 1. Làm sạch dữ liệu sang Silver
python spark_jobs/transform/process_silver.py

# 2. Thống kê kinh doanh sang Gold
python spark_jobs/transform/process_gold.py
```

### Bước 5: Khởi chạy Luồng Chấm điểm Thời gian thực (cham_diem.py)
```cmd
python spark_jobs/streaming/cham_diem.py
```

### Bước 6: Khởi chạy Backend FastAPI & Web Dashboard
1. Bật máy chủ API Backend:
   ```cmd
   uvicorn webapp.backend.main:app --reload --port 8000
   ```
2. Mở file `index.html` trên trình duyệt hoặc truy cập `http://127.0.0.1:8000/docs` xem Swagger UI.

---

## 🔄 TỰ ĐỘNG HÓA PIPELINE VỚI APACHE AIRFLOW
Kích hoạt DAG điều phối tự động các task: `task_check_hdfs` ➔ `task_ingest_kafka` ➔ `task_spark_silver` ➔ `task_train_ml` ➔ `task_spark_gold`.

---

## 📦 HƯỚNG DẪN PUSH CODE LÊN GIT (GIT WORKFLOW)
```cmd
git status
git add .
git commit -m "Hoan thien he thong Real-time Fraud Detection Lakehouse"
git push origin main
```

---

## 👥 TÁC GIẢ & BẢO QUYỀN
- **Sinh viên thực hiện:** Lê Thanh Phong
- **GitHub Repository:** `kbt2981-ux`
- **Môn học:** Công nghệ Dữ liệu lớn (Big Data)
