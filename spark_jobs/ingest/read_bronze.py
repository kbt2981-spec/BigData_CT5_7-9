import os
import sys
import time
from delta.tables import DeltaTable

os.environ['JAVA_HOME'] = r'D:\Homework\Java\OpenJDK17U-jdk_x64_windows_hotspot_17.0.20.1_1\jdk-17.0.20.1+1'
os.environ['HADOOP_HOME'] = r'D:\Homework\Hadoop'
os.environ['PYSPARK_PYTHON'] = sys.executable
os.environ['PYSPARK_DRIVER_PYTHON'] = sys.executable

from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("ReadBronzeData") \
    .master("local[*]") \
    .config("spark.driver.memory", "1g") \
    .config("spark.executor.memory", "1g") \
    .config("spark.jars.packages", "io.delta:delta-spark_2.12:3.1.0") \
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

bronze_path = "./delta_lake/bronze/giao_dich"

print(f"[*] Đang kiểm tra dữ liệu Bronze tại: {bronze_path}")
while not DeltaTable.isDeltaTable(spark, bronze_path):
    print("[!] Chưa tìm thấy bảng Delta Bronze hợp lệ. Chờ 5 giây...")
    time.sleep(5)

print("[*] Đã tìm thấy dữ liệu Bronze. Tiến hành đọc...")
df = spark.read.format("delta").load(bronze_path)

print(f"--- Tổng số dòng hiện có trong Bronze: {df.count()} ---")
df.show(5, truncate=False)
df.printSchema()