@echo off
chcp 65001 >nul
echo ===================================================
echo [0] Dọn dẹp toàn bộ dữ liệu, mô hình và checkpoint cũ...
echo ===================================================
if exist delta_lake rmdir /s /q delta_lake
if exist models rmdir /s /q models
if exist checkpoints rmdir /s /q checkpoints
echo Đã làm sạch toàn bộ môi trường!

echo ===================================================
echo [1] Khởi động hạ tầng Docker (Kafka + Zookeeper)...
echo ===================================================
docker-compose up -d
echo Đang chờ Kafka khởi động (25 giây)...
timeout /t 25 /nobreak

echo ===================================================
echo [2] Khởi tạo Kafka Topic...
echo ===================================================
.\.venv\Scripts\python.exe spark_jobs\ingest\create_topic.py
timeout /t 3 /nobreak

echo ===================================================
echo [3] Kích hoạt Producer bơm dữ liệu vào Kafka...
echo ===================================================
start "Kafka Producer" cmd /k ".\.venv\Scripts\python.exe spark_jobs\ingest\producer.py"
timeout /t 8 /nobreak

echo ===================================================
echo [4] Chạy Consumer Bronze (Thu thập dữ liệu thô)...
echo ===================================================
start "Consumer Bronze" cmd /k ".\.venv\Scripts\python.exe spark_jobs\ingest\consumer_bronze.py"
echo Đang chờ Consumer Bronze tích lũy dữ liệu thô (15 giây)...
timeout /t 15 /nobreak

echo ===================================================
echo [5] Chạy tuần tự ETL: Bronze -> Silver -> Gold...
echo ===================================================
echo Đang chạy Process Silver (Chạy đồng bộ)...
.\.venv\Scripts\python.exe spark_jobs\transform\process_silver.py

echo Đang chạy Process Gold (Chạy đồng bộ)...
.\.venv\Scripts\python.exe spark_jobs\transform\process_gold.py

echo ===================================================
echo [6] Huấn luyện mô hình Machine Learning (Train Model)...
echo ===================================================
:: Chạy đồng bộ trực tiếp để đảm bảo file model chắc chắn được sinh ra 100%%
.\.venv\Scripts\python.exe spark_jobs\ml\train_model.py

echo ===================================================
echo [7] Kích hoạt các luồng Streaming và Web App...
echo ===================================================
start "Cap Nhat Trang Thai" cmd /k ".\.venv\Scripts\python.exe spark_jobs\streaming\cap_nhat_trang_thai.py"
timeout /t 5 /nobreak

start "Real-time Scoring" cmd /k ".\.venv\Scripts\python.exe spark_jobs\streaming\cham_diem.py"
timeout /t 5 /nobreak

start "FastAPI Backend" cmd /k "cd /d webapp\backend && ..\..\.venv\Scripts\python.exe -m uvicorn main:app --reload --port 8000"

echo ===================================================
echo HOÀN TẤT KHỞI CHẠY HỆ THỐNG THÀNH CÔNG!
echo ===================================================
pause