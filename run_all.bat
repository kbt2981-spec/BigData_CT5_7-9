@echo off
echo ===================================================
echo [1] Khoi dong ha tang Kafka, Zookeeper qua Docker...
echo ===================================================
docker-compose up -d

echo Dang cho Docker/Kafka khoi dong hoan toan (20 giay)...
timeout /t 20 /nobreak

echo ===================================================
echo [2] Khoi tao Kafka Topic...
echo ===================================================
.\.venv\Scripts\python.exe create_topic.py
timeout /t 3 /nobreak

echo ===================================================
echo [3] Kich hoat PRODUCER de bom du lieu moi...
echo ===================================================
start "Kafka Producer" cmd /k ".\.venv\Scripts\python.exe producer.py"

echo Dang doi Producer bom nhung record dau tien vao Kafka (15 giay)...
timeout /t 15 /nobreak

echo ===================================================
echo [4] Chay luong BRONZE (Ghi du lieu tu Kafka xuong Delta)...
echo ===================================================
start "Consumer Bronze" cmd /k ".\.venv\Scripts\python.exe consumer_bronze.py"

echo Dang doi Bronze tao thu muc va ghi file _delta_log (20 giay)...
timeout /t 20 /nobreak

echo ===================================================
echo [5] Chay luong TRANG THAI va SILVER...
echo ===================================================
start "Cap Nhat Trang Thai" cmd /k ".\.venv\Scripts\python.exe cap_nhat_trang_thai.py"
timeout /t 8 /nobreak

start "Process Silver" cmd /k ".\.venv\Scripts\python.exe process_silver.py"

echo Dang doi Silver tao thu muc va ghi du lieu (20 giay)...
timeout /t 20 /nobreak

echo ===================================================
echo [6] Chay luong GOLD...
echo ===================================================
start "Process Gold" cmd /k ".\.venv\Scripts\python.exe process_gold.py"

echo Dang doi Gold tong hop dac trung ban dau (30 giay)...
timeout /t 30 /nobreak

echo ===================================================
echo [7] Huan luyen mo hinh Machine Learning...
echo ===================================================
:: Chay batch de huan luyen mo hinh 1 lan dua tren du lieu Gold hien co
:: Su dung cmd /c vi day la tac vu batch, chay xong se tu tat terminal
start "Train Model" cmd /c ".\.venv\Scripts\python.exe train_model.py"

echo Dang doi huan luyen mo hinh va luu vao thu muc models (40 giay)...
timeout /t 40 /nobreak

echo ===================================================
echo [8] Kich hoat he thong CHAM DIEM GIAN LAN REAL-TIME...
echo ===================================================
:: Luong streaming nay se nap model da train va score truc tiep cac giao dich moi
start "Real-time Scoring" cmd /k ".\.venv\Scripts\python.exe cham_diem.py"

echo ===================================================
echo HOAN TAT KHOI CHAY HE THONG GIAN LAN TOAN DIEN!
echo ===================================================
pause