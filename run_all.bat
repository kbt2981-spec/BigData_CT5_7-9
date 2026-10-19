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
docker info >nul 2>&1
if %errorlevel% neq 0 goto :launch_docker
goto :docker_is_ready

:launch_docker
echo [!] Phat hien Docker Desktop chua hoat dong!
echo Dang khoi dong Docker Desktop, vui long cho...
if exist "C:\Users\lepho\AppData\Local\Programs\DockerDesktop\Docker Desktop.exe" start "" "C:\Users\lepho\AppData\Local\Programs\DockerDesktop\Docker Desktop.exe"
echo Dang cho Docker Engine khoi dong...
timeout /t 35 /nobreak

:docker_is_ready
docker-compose up -d
echo Đang chờ Kafka & Zookeeper khởi động sẵn sàng (15 giây)...
timeout /t 15 /nobreak

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
echo [6] Tạo tập đặc trưng Point-in-time & Huấn luyện ML...
echo ===================================================
echo Đang tính toán đặc trưng lịch sử Point-in-time (chống Data Leakage)...
.\.venv\Scripts\python.exe spark_jobs\ml\tao_tap_huan_luyen.py

echo Đang huấn luyện & so sánh các mô hình Machine Learning...
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