from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
import os
import time

default_args = {
    'owner': 'fraud_team',
    'depends_on_past': False,
    'start_date': datetime(2026, 1, 1),
    'retries': 1,
}

# Đường dẫn thư mục Gold chứa dữ liệu Delta Lake
# Dùng /mnt/d/... nếu Airflow chạy trên WSL, hoặc D:/... nếu test script thuần
GOLD_DIR = "/mnt/d/Homework/BigData_CT5_7-9/delta_lake/gold_diem_rui_ro/_delta_log"

def check_streaming_by_file_update():
    if not os.path.exists(GOLD_DIR):
        print(f"[WARNING] Không tìm thấy thư mục: {GOLD_DIR}")
        return "Not Found"
        
    # Lấy thời gian chỉnh sửa cuối cùng của thư mục _delta_log
    last_modified_time = os.path.getmtime(GOLD_DIR)
    current_time = time.time()
    
    # Nếu không có dữ liệu mới trong 15 phút (900s), coi như Streaming đã sập
    time_diff = current_time - last_modified_time
    if time_diff > 900:
        print(f"[ALERT] Streaming job có thể đã sập! Không có dữ liệu mới trong {time_diff/60:.2f} phút.")
        # Chèn code gửi email cảnh báo hoặc trigger khởi động lại tại đây
        return "Streaming Dead"
        
    print(f"[INFO] Streaming hoạt động tốt. Dữ liệu mới cập nhật {(time_diff/60):.2f} phút trước.")
    return "Streaming Alive"

with DAG(
    'gl_giam_sat_streaming',
    default_args=default_args,
    description='Giám sát Spark Streaming bằng cách kiểm tra file Delta update',
    schedule_interval='*/10 * * * *',
    catchup=False,
) as dag:

    monitor_task = PythonOperator(
        task_id='check_streaming_health',
        python_callable=check_streaming_by_file_update,
    )