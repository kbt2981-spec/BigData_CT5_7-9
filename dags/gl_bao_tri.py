from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator

default_args = {
    'owner': 'fraud_team',
    'start_date': datetime(2026, 1, 1),
    'retries': 1,
}

PROJECT_DIR = "D:/Homework/BigData_CT5_7-9"

with DAG(
    'gl_bao_tri',
    default_args=default_args,
    description='Bảo trì Delta Lake: OPTIMIZE, ZORDER BY, VACUUM hàng tuần',
    schedule_interval='0 2 * * 0',
    catchup=False,
) as dag:

    optimize_delta = BashOperator(
        task_id='optimize_and_zorder',
        bash_command=f'''
        python3 -c "
from pyspark.sql import SparkSession
spark = SparkSession.builder \\
    .appName('DeltaMaintenance') \\
    .config('spark.sql.extensions', 'io.delta.sql.DeltaSparkSessionExtension') \\
    .config('spark.sql.catalog.spark_catalog', 'org.apache.spark.sql.delta.catalog.DeltaCatalog') \\
    .getOrCreate()

spark.sql('OPTIMIZE delta.\`{PROJECT_DIR}/delta_lake/silver_trang_thai\` ZORDER BY (tai_khoan_nguon, thoi_diem)')
spark.sql('OPTIMIZE delta.\`{PROJECT_DIR}/delta_lake/gold_diem_rui_ro\` ZORDER BY (tai_khoan_nguon, thoi_diem)')
print('OPTIMIZE + ZORDER completed.')
"
        ''',
    )

    vacuum_delta = BashOperator(
        task_id='vacuum_old_files',
        bash_command=f'''
        python3 -c "
from pyspark.sql import SparkSession
spark = SparkSession.builder \\
    .appName('DeltaVacuum') \\
    .config('spark.sql.extensions', 'io.delta.sql.DeltaSparkSessionExtension') \\
    .config('spark.sql.catalog.spark_catalog', 'org.apache.spark.sql.delta.catalog.DeltaCatalog') \\
    .getOrCreate()

spark.conf.set('spark.databricks.delta.vacuum.parallelDelete.enabled', 'true')
spark.sql('VACUUM delta.\`{PROJECT_DIR}/delta_lake/silver_trang_thai\` RETAIN 168 HOURS')
spark.sql('VACUUM delta.\`{PROJECT_DIR}/delta_lake/gold_diem_rui_ro\` RETAIN 168 HOURS')
print('VACUUM completed.')
"
        ''',
    )

    optimize_delta >> vacuum_delta