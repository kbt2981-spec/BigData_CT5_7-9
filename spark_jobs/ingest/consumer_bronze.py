import os
import sys

JAVA_HOME = r"D:\Homework\Java\OpenJDK17U-jdk_x64_windows_hotspot_17.0.20.1_1\jdk-17.0.20.1+1"
HADOOP_HOME = r"D:\Homework\Hadoop"

# Kiem tra duong dan he thong
java_exe_path = os.path.join(JAVA_HOME, "bin", "java.exe")
winutils_path = os.path.join(HADOOP_HOME, "bin", "winutils.exe")

if not os.path.exists(java_exe_path):
    raise FileNotFoundError(f"\n[LOI NGHIEM TRONG]: Khong tim thay java.exe tai {java_exe_path}")

if not os.path.exists(winutils_path):
    raise FileNotFoundError(f"\n[LOI NGHIEM TRONG]: Khong tim thay winutils.exe tai {winutils_path}")

os.environ["JAVA_HOME"] = JAVA_HOME
os.environ["HADOOP_HOME"] = HADOOP_HOME
os.environ["PATH"] = os.path.join(HADOOP_HOME, "bin") + ";" + os.environ.get("PATH", "")

venv_python = sys.executable 
os.environ["PYSPARK_PYTHON"] = venv_python
os.environ["PYSPARK_DRIVER_PYTHON"] = venv_python

# Giai phap triet de: Khai bao bien moi truong de ep Spark tai goi Kafka va Delta truoc khi khoi tao
os.environ['PYSPARK_SUBMIT_ARGS'] = '--packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,io.delta:delta-spark_2.12:3.1.0 pyspark-shell'

sys.setrecursionlimit(15000)

import socket
import time
from pyspark.sql import SparkSession
from pyspark.sql.functions import current_timestamp
from delta import configure_spark_with_delta_pip

def check_kafka_connection(host="127.0.0.1", port=9092, timeout=3):
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except (socket.timeout, ConnectionRefusedError, OSError):
        return False

def main():
    print("==========================================================================")
    print(" [CONSUMER BRONZE] KHOI CHAY LUONG THU THAP DU LIEU THO TU KAFKA")
    print("==========================================================================")
    
    # 1. Kiem tra tinh san sang cua Apache Kafka truoc khi khoi tao Spark
    print("--> Dang kiem tra ket noi toi Kafka Broker tai localhost:9092...")
    retry_count = 0
    while not check_kafka_connection("localhost", 9092, timeout=2):
        retry_count += 1
        print(f"[!] Chua tim thay Kafka Broker tai localhost:9092 (Lan thu {retry_count}/4)...")
        if retry_count >= 4:
            print("\n" + "="*75)
            print(" [LỖI KẾT NỐI KAFKA BROKER]:")
            print(" Không thể kết nối tới Apache Kafka tại localhost:9092!")
            print(" NGUYÊN NHÂN:")
            print("   - Docker Desktop chưa được bật trên máy tính.")
            print("   - Hoặc các container Kafka/Zookeeper chưa chạy.")
            print(" CÁCH KHẮC PHỤC:")
            print("   1. Mở ứng dụng Docker Desktop trên màn hình Desktop hoặc Start Menu.")
            print("   2. Chờ biểu tượng cá voi chuyển sang màu xanh (Engine running).")
            print("   3. Chạy lệnh: docker-compose up -d")
            print("   4. Chạy lại script này hoặc .\\run_all.bat")
            print("="*75 + "\n")
            sys.exit(1)
        time.sleep(3)
    
    print("--> Da ket noi toi Kafka Broker thanh cong! Bat dau khoi tao Spark Session...")

    builder = SparkSession.builder \
        .appName("ConsumerBronze") \
        .master("local[*]") \
        .config("spark.driver.host", "127.0.0.1") \
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
        .config("spark.driver.memory", "2g") \
        .config("spark.executor.memory", "2g") \
        .config("spark.driver.extraJavaOptions", 
                "--add-opens=java.base/java.lang=ALL-UNNAMED "
                "--add-opens=java.base/java.lang.invoke=ALL-UNNAMED "
                "--add-opens=java.base/java.lang.reflect=ALL-UNNAMED "
                "--add-opens=java.base/java.io=ALL-UNNAMED "
                "--add-opens=java.base/java.net=ALL-UNNAMED "
                "--add-opens=java.base/java.nio=ALL-UNNAMED "
                "--add-opens=java.base/java.util=ALL-UNNAMED "
                "--add-opens=java.base/java.util.concurrent=ALL-UNNAMED "
                "--add-opens=java.base/sun.nio.ch=ALL-UNNAMED")

    spark = configure_spark_with_delta_pip(builder).getOrCreate()
    spark.sparkContext.setLogLevel("WARN")

    # Đã đổi từ "latest" thành "earliest" để đọc từ đầu, lấy cả dữ liệu lịch sử có chứa mẫu gian lận
    df_kafka = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "localhost:9092") \
        .option("subscribe", "transactions") \
        .option("startingOffsets", "earliest") \
        .load()

    # Chuyen doi du lieu tho va them moc thoi gian nhan
    df_bronze = df_kafka \
        .selectExpr("CAST(value AS STRING) as json_value", "timestamp as kafka_timestamp") \
        .withColumn("thoi_diem_nhan", current_timestamp())

    BRONZE_TABLE_PATH = "./delta_lake/bronze/giao_dich"
    CHECKPOINT_PATH = "./checkpoints/bronze_giao_dich"

    # Ghi vao tang Bronze duoi dinh dang Delta Lake (Append-only)
    query = df_bronze.writeStream \
        .format("delta") \
        .outputMode("append") \
        .option("checkpointLocation", CHECKPOINT_PATH) \
        .start(BRONZE_TABLE_PATH)

    query.awaitTermination()

if __name__ == "__main__":
    main()