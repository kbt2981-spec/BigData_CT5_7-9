from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.operators.python import PythonOperator
import os

default_args = {
    'owner': 'fraud_team',
    'start_date': datetime(2026, 1, 1),
    'retries': 1,
}

PROJECT_DIR = "D:/Homework/BigData_CT5_7-9"

with DAG(
    'gl_kiem_tra_drift',
    default_args=default_args,
    description='Tính PSI & KS-statistic hàng ngày, ghi nhận vào gold.theo_doi_drift',
    schedule_interval='0 1 * * *',
    catchup=False,
) as dag:

    calculate_drift = BashOperator(
        task_id='calculate_psi_ks',
        bash_command=f'cd {PROJECT_DIR} && python3 -m scripts.tinh_drift',
    )

    trigger_retrain = TriggerDagRunOperator(
        task_id='trigger_retrain_if_drift',
        trigger_dag_id='gl_huan_luyen_lai',
        execution_date='{{ execution_date }}',
        reset_dag_run=True,
    )

    calculate_drift >> trigger_retrain