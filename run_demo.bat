@echo off
chcp 65001 >nul
echo ===================================================
echo   FRAUDGUARD AI - DEMO NHANH (Khong train lai)
echo   Su dung data va mo hinh da co san
echo ===================================================

REM -------------------------------------------------------
REM Kiem tra xem da co model va data chua
REM -------------------------------------------------------
echo [0] Kiem tra du lieu va mo hinh san co...
if not exist "models\gbt_fraud_model" (
    echo [!] CANH BAO: Chua tim thay mo hinh tai models\gbt_fraud_model
    echo [!] Vui long chay run_all.bat truoc de train mo hinh.
    echo [!] Sau do chay lai run_demo.bat nay.
    pause
    exit /b 1
)
if not exist "delta_lake\silver\giao_dich" (
    echo [!] CANH BAO: Chua tim thay du lieu Silver Delta Lake.
    echo [!] Vui long chay run_all.bat truoc de khoi tao du lieu.
    pause
    exit /b 1
)
echo [+] Mo hinh san co:    models\gbt_fraud_model
echo [+] Du lieu san co:    delta_lake\silver\giao_dich
echo.

REM -------------------------------------------------------
REM Buoc 1: Khoi dong Docker (neu chua chay)
REM -------------------------------------------------------
echo ===================================================
echo [1] Kiem tra va khoi dong ha tang Docker...
echo ===================================================
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Docker Desktop chua hoat dong! Dang khoi dong...
    if exist "C:\Users\lepho\AppData\Local\Programs\DockerDesktop\Docker Desktop.exe" (
        start "" "C:\Users\lepho\AppData\Local\Programs\DockerDesktop\Docker Desktop.exe"
    )
    echo Dang cho Docker Engine san sang (35 giay)...
    timeout /t 35 /nobreak
)

docker-compose up -d
echo Dang cho cac container on dinh (15 giay)...
timeout /t 15 /nobreak
echo.

REM -------------------------------------------------------
REM Buoc 2: Tao Kafka Topic (neu chua co)
REM -------------------------------------------------------
echo ===================================================
echo [2] Khoi tao Kafka Topic (neu chua ton tai)...
echo ===================================================
.\.venv\Scripts\python.exe spark_jobs\ingest\create_topic.py
timeout /t 3 /nobreak
echo.

REM -------------------------------------------------------
REM Buoc 3: Bat Producer (bom du lieu moi vao Kafka)
REM -------------------------------------------------------
echo ===================================================
echo [3] Kich hoat Producer bom giao dich moi...
echo ===================================================
start "Kafka Producer" cmd /k ".\.venv\Scripts\python.exe spark_jobs\ingest\producer.py"
echo Dang cho Producer khoi dong (8 giay)...
timeout /t 8 /nobreak
echo.

REM -------------------------------------------------------
REM Buoc 4: Bat Consumer Bronze (luu du lieu thô moi)
REM -------------------------------------------------------
echo ===================================================
echo [4] Kich hoat Consumer Bronze...
echo ===================================================
start "Consumer Bronze" cmd /k ".\.venv\Scripts\python.exe spark_jobs\ingest\consumer_bronze.py"
echo Dang cho Consumer Bronze san sang (10 giay)...
timeout /t 10 /nobreak
echo.

REM -------------------------------------------------------
REM Buoc 5: Bat Streaming (dung mo hinh da train san)
REM -------------------------------------------------------
echo ===================================================
echo [5] Kich hoat Spark Streaming (dung mo hinh san co)...
echo ===================================================
start "Cap Nhat Trang Thai" cmd /k ".\.venv\Scripts\python.exe spark_jobs\streaming\cap_nhat_trang_thai.py"
timeout /t 5 /nobreak

start "Real-time Scoring" cmd /k ".\.venv\Scripts\python.exe spark_jobs\streaming\cham_diem.py"
timeout /t 5 /nobreak
echo.

REM -------------------------------------------------------
REM Buoc 6: Bat FastAPI Web App
REM -------------------------------------------------------
echo ===================================================
echo [6] Kich hoat FastAPI Backend va Web Dashboard...
echo ===================================================
start "FastAPI Backend" cmd /k "cd /d webapp\backend && ..\..\\.venv\Scripts\python.exe -m uvicorn main:app --reload --port 8000"
timeout /t 3 /nobreak

REM Mo trinh duyet tu dong
echo Dang mo Web Dashboard tren trinh duyet...
timeout /t 3 /nobreak
start "" "http://127.0.0.1:5500/webapp/frontend/index.html"
timeout /t 2 /nobreak
start "" "http://127.0.0.1:8000/docs"
echo.

echo ===================================================
echo   HE THONG DEMO DA SAN SANG!
echo ===================================================
echo   Web Dashboard : http://127.0.0.1:5500/webapp/frontend/index.html
echo   FastAPI Docs  : http://127.0.0.1:8000/docs
echo   Kafka Producer: Dang chay (bom du lieu moi lien tuc)
echo   Streaming     : Dang chay (cham diem gian lan real-time)
echo ===================================================
echo   [!] Luu y: Day la che do DEMO NHANH.
echo       Mo hinh va du lieu lich su duoc giu nguyen.
echo       De train lai tu dau: dung run_all.bat
echo ===================================================
pause
