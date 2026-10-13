from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator

default_args = {
    'owner': 'fraud_team',
    'start_date': datetime(2026, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

PROJECT_DIR = "D:/Homework/BigData_CT5_7-9"

with DAG(
    'gl_huan_luyen_lai',
    default_args=default_args,
    description='Tự động huấn luyện lại GBTClassifier khi bị Drift hoặc có nhãn mới',
    schedule_interval=None,
    catchup=False,
) as dag:

    retrain_model = BashOperator(
        task_id='run_train_model',
        bash_command=f'cd {PROJECT_DIR} && python3 train_model.py',
    )

    evaluate_and_promote = BashOperator(
        task_id='evaluate_and_promote_model',
        bash_command=f'cd {PROJECT_DIR} && python3 spark_jobs/ml/train_model.py',
    )

    retrain_model >> evaluate_and_promote