@echo off
echo [1] Dang dung toan bo cac tien trinh Python (PySpark & Producer)...
taskkill /F /IM python.exe /T

echo [2] Dang dung va xoa ha tang Docker (Kafka & Zookeeper)...
docker-compose down

echo ===================================================
echo DA TAT SACH TOAN BO HE THONG THANH CONG!
echo ===================================================
pause