@echo off
chcp 65001 >nul

echo =================================================
echo   FRAUDGUARD AI ^- DEMO NHANH (khong train lai)
echo   Dung data va mo hinh da co san
echo =================================================
echo.

REM --- Kiem tra model ---
echo [0] Kiem tra mo hinh va du lieu san co...
if not exist "models\gbt_fraud_model\metadata" (
    echo [!] CANH BAO: Chua co mo hinh tai models\gbt_fraud_model
    echo [!] Hay chay run_all.bat truoc de train mo hinh lan dau.
    echo [!] Sau do chay lai run_demo.bat.
    pause
    exit /b 1
)
if not exist "delta_lake\silver" (
    echo [!] CANH BAO: Chua co du lieu Silver Delta Lake.
    echo [!] Hay chay run_all.bat truoc de khoi tao du lieu.
    pause
    exit /b 1
)
echo [OK] Mo hinh:   models\gbt_fraud_model
echo [OK] Du lieu:   delta_lake\silver
echo.

REM --- Docker ---
echo =================================================
echo [1] Kiem tra va khoi dong Docker...
echo =================================================
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo Docker Desktop chua chay! Dang khoi dong...
    if exist "C:\Users\lepho\AppData\Local\Programs\DockerDesktop\Docker Desktop.exe" (
        start "" "C:\Users\lepho\AppData\Local\Programs\DockerDesktop\Docker Desktop.exe"
    )
    timeout /t 35 /nobreak >nul
)
docker-compose up -d
echo Cho cac container on dinh (15 giay)...
timeout /t 15 /nobreak >nul
echo.

REM --- Kafka Topic ---
echo =================================================
echo [2] Khoi tao Kafka Topic (neu chua co)...
echo =================================================
.\.venv\Scripts\python.exe spark_jobs\ingest\create_topic.py
timeout /t 3 /nobreak >nul
echo.

REM --- Producer ---
echo =================================================
echo [3] Bat Producer bom giao dich moi vao Kafka...
echo =================================================
start "Kafka Producer" cmd /k ".\.venv\Scripts\python.exe spark_jobs\ingest\producer.py"
timeout /t 8 /nobreak >nul
echo.

REM --- Consumer Bronze ---
echo =================================================
echo [4] Bat Consumer Bronze...
echo =================================================
start "Consumer Bronze" cmd /k ".\.venv\Scripts\python.exe spark_jobs\ingest\consumer_bronze.py"
timeout /t 10 /nobreak >nul
echo.

REM --- Streaming (dung model san) ---
echo =================================================
echo [5] Bat Spark Streaming (dung mo hinh san co)...
echo =================================================
start "Cap Nhat Trang Thai" cmd /k ".\.venv\Scripts\python.exe spark_jobs\streaming\cap_nhat_trang_thai.py"
timeout /t 5 /nobreak >nul
start "Real-time Scoring" cmd /k ".\.venv\Scripts\python.exe spark_jobs\streaming\cham_diem.py"
timeout /t 5 /nobreak >nul
echo.

REM --- FastAPI ---
echo =================================================
echo [6] Bat FastAPI Backend...
echo =================================================
start "FastAPI Backend" cmd /k "cd /d webapp\backend && ..\..\\.venv\Scripts\python.exe -m uvicorn main:app --reload --port 8000"
timeout /t 5 /nobreak >nul

REM --- Mo trinh duyet ---
echo Mo Web Dashboard tren trinh duyet...
start "" "http://127.0.0.1:5500/webapp/frontend/index.html"
timeout /t 2 /nobreak >nul
start "" "http://127.0.0.1:8000/docs"
echo.

echo =================================================
echo   HE THONG DEMO DA SAN SANG!
echo =================================================
echo   Web Dashboard : http://127.0.0.1:5500/webapp/frontend/index.html
echo   FastAPI Docs  : http://127.0.0.1:8000/docs
echo =================================================
echo   De train lai tu dau: chay run_all.bat
echo =================================================
pause
