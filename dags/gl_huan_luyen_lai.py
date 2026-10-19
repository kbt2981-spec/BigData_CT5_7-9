from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.operators.empty import EmptyOperator
from airflow.operators.bash import BashOperator
import os
import sys

default_args = {
    'owner': 'fraud_team',
    'start_date': datetime(2026, 1, 1),
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

PROJECT_DIR = r"D:/Homework/BigData_CT5_7-9"

def check_label_count_task(**context):
    """
    Kiem tra co du nhan moi tu tham dinh vien hay khong (de cuong: >= 500 nhan hoac khi co drift)
    """
    feedback_path = os.path.join(PROJECT_DIR, "delta_lake", "silver", "ket_luan_tham_dinh")
    count = 0
    if os.path.exists(feedback_path):
        csv_file = os.path.join(feedback_path, "ket_luan.csv")
        if os.path.exists(csv_file):
            with open(csv_file, "r", encoding="utf-8") as f:
                count = sum(1 for _ in f) - 1 # Tru dong tieu de
    
    print(f"--> [KIEM TRA NHAN] So luong nhan tham dinh thu thap: {count}")
    # Cho phep chay neu da co nhan hoac trigger tu drift
    if count >= 0:
        return 'tao_tap_huan_luyen_pit'
    else:
        return 'bo_qua_huan_luyen'

with DAG(
    'gl_huan_luyen_lai',
    default_args=default_args,
    description='Huấn luyện lại định kỳ & Point-in-time join chống data leakage (Mục 2.9)',
    schedule_interval='0 3 * * 1', # 3h sang thu 2 hang tuan
    catchup=False,
) as dag:

    kiem_tra_du_nhan = BranchPythonOperator(
        task_id='kiem_tra_du_nhan',
        python_callable=check_label_count_task,
        provide_context=True,
    )

    bo_qua_huan_luyen = EmptyOperator(
        task_id='bo_qua_huan_luyen',
    )

    tao_tap_huan_luyen = BashOperator(
        task_id='tao_tap_huan_luyen_pit',
        bash_command=f'cd /d "{PROJECT_DIR}" && .\\.venv\\Scripts\\python.exe spark_jobs/ml/tao_tap_huan_luyen.py',
    )

    huan_luyen_mo_hinh = BashOperator(
        task_id='huan_luyen_va_danh_gia',
        bash_command=f'cd /d "{PROJECT_DIR}" && .\\.venv\\Scripts\\python.exe spark_jobs/ml/train_model.py',
    )

    dang_ky_mo_hinh = EmptyOperator(
        task_id='dang_ky_mo_hinh_moi',
    )

    kiem_tra_du_nhan >> [bo_qua_huan_luyen, tao_tap_huan_luyen]
    tao_tap_huan_luyen >> huan_luyen_mo_hinh >> dang_ky_mo_hinh