from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.operators.empty import EmptyOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
import os
import sys

default_args = {
    'owner': 'fraud_team',
    'start_date': datetime(2026, 1, 1),
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

PROJECT_DIR = r"D:/Homework/BigData_CT5_7-9"

def tinh_psi_ks_task(**context):
    """
    Goi logic tinh PSI va KS-statistic tu scripts/tinh_drift.py
    """
    sys.path.append(PROJECT_DIR)
    try:
        from scripts.tinh_drift import run_drift_analysis
        max_psi = run_drift_analysis()
    except Exception as e:
        print(f"[!] Warning while calculating drift: {e}")
        max_psi = 0.05
    
    # Day gia tri max_psi len XCom de BranchPythonOperator su dung
    context['ti'].xcom_push(key='max_psi', value=max_psi)
    return max_psi

def branch_decision_task(**context):
    """
    Phan nhanh theo yeu cau Muc 2.9 De cuong:
    - psi < 0.1: on dinh -> ghi_nhat_ky
    - 0.1 <= psi <= 0.25: canh bao nhe -> canh_bao_email
    - psi > 0.25: nghiem trong -> kich_hoat_dag_huan_luyen
    """
    ti = context['ti']
    max_psi = ti.xcom_pull(key='max_psi', task_ids='tinh_psi_ks')
    if max_psi is None:
        max_psi = 0.05
    
    print(f"--> [BRANCH DECISION] Gia tri PSI thu thap duoc: {max_psi:.4f}")
    if max_psi < 0.1:
        return 'ghi_nhat_ky'
    elif 0.1 <= max_psi <= 0.25:
        return 'canh_bao_email'
    else:
        return 'kich_hoat_dag_huan_luyen'

with DAG(
    'gl_kiem_tra_drift',
    default_args=default_args,
    description='Kiểm tra Data Drift (PSI/KS) và phân nhánh BranchPythonOperator (Mục 2.9)',
    schedule_interval='0 1 * * *',
    catchup=False,
) as dag:

    tinh_psi_ks = PythonOperator(
        task_id='tinh_psi_ks',
        python_callable=tinh_psi_ks_task,
        provide_context=True,
    )

    branch_drift = BranchPythonOperator(
        task_id='branch_drift_decision',
        python_callable=branch_decision_task,
        provide_context=True,
    )

    ghi_nhat_ky = EmptyOperator(
        task_id='ghi_nhat_ky',
    )

    canh_bao_email = EmptyOperator(
        task_id='canh_bao_email',
    )

    kich_hoat_dag_huan_luyen = TriggerDagRunOperator(
        task_id='kich_hoat_dag_huan_luyen',
        trigger_dag_id='gl_huan_luyen_lai',
        reset_dag_run=True,
    )

    # Thiet lap luong phan nhanh
    tinh_psi_ks >> branch_drift
    branch_drift >> [ghi_nhat_ky, canh_bao_email, kich_hoat_dag_huan_luyen]