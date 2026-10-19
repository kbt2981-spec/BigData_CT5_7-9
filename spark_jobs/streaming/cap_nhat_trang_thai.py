import os
import sys

JAVA_HOME = r"D:\Homework\Java\OpenJDK17U-jdk_x64_windows_hotspot_17.0.20.1_1\jdk-17.0.20.1+1"
HADOOP_HOME = r"D:\Homework\Hadoop"

# --- TRINH KIEM TRA DUONG DAN ---
java_exe_path = os.path.join(JAVA_HOME, "bin", "java.exe")
winutils_path = os.path.join(HADOOP_HOME, "bin", "winutils.exe")

if not os.path.exists(java_exe_path):
    raise FileNotFoundError(f"\n[LOI NGHIEM TRONG]: Khong tim thay java.exe tai {java_exe_path}")

if not os.path.exists(winutils_path):
    raise FileNotFoundError(f"\n[LOI NGHIEM TRONG]: Khong tim thay winutils.exe tai {winutils_path}")

os.environ["JAVA_HOME"] = JAVA_HOME
os.environ["HADOOP_HOME"] = HADOOP_HOME

java_bin = os.path.join(JAVA_HOME, "bin")
hadoop_bin = os.path.join(HADOOP_HOME, "bin")
os.environ["PATH"] = java_bin + os.path.pathsep + hadoop_bin + os.path.pathsep + os.environ.get("PATH", "")

venv_python = sys.executable 
os.environ["PYSPARK_PYTHON"] = venv_python
os.environ["PYSPARK_DRIVER_PYTHON"] = venv_python
sys.setrecursionlimit(15000)

from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, current_timestamp, count, sum as spark_sum, max as spark_max
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, TimestampType

def main():
    spark = SparkSession.builder \
        .appName("FraudStateManagementComplete") \
        .master("local[*]") \
        .config("spark.driver.host", "127.0.0.1") \
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
        .config("spark.jars.packages", "io.delta:delta-spark_2.12:3.2.0,org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0") \
        .config("spark.driver.memory", "2g") \
        .config("spark.executor.memory", "2g") \
        .getOrCreate()

    spark.sparkContext.setLogLevel("WARN")
    spark.sql("CREATE DATABASE IF NOT EXISTS silver")

    kafka_schema = StructType([
        StructField("tai_khoan_nguon", StringType(), True),
        StructField("so_tien", DoubleType(), True),
        StructField("thoi_diem", TimestampType(), True)
    ])

    kafka_stream_df = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "localhost:9092") \
        .option("subscribe", "transactions") \
        .option("startingOffsets", "latest") \
        .load()

    parsed_df = kafka_stream_df.select(
        from_json(col("value").cast("string"), kafka_schema).alias("data")
    ).select("data.*")

    # Tong hop trang thai voi outputMode("complete")
    aggregated_df = parsed_df \
        .groupBy("tai_khoan_nguon") \
        .agg(
            count("*").alias("so_gd_24h"),
            spark_sum("so_tien").alias("tong_tien_24h"),
            spark_max("thoi_diem").alias("lan_gd_gan_nhat")
        ) \
        .withColumn("cap_nhat_luc", current_timestamp()) \
        .withColumnRenamed("tai_khoan_nguon", "tai_khoan")

    SILVER_TABLE_PATH = "./delta_lake/silver/trang_thai_khach_hang"
    CHECKPOINT_PATH = "./checkpoints/cap_nhat_trang_thai"

    from delta.tables import DeltaTable

    def write_complete_batch(batch_df, batch_id):
        if batch_df.isEmpty():
            return

        # Ap dung chuan MERGE INTO theo yeu cau Muc 2.7 de cuong
        if DeltaTable.isDeltaTable(spark, SILVER_TABLE_PATH):
            target_table = DeltaTable.forPath(spark, SILVER_TABLE_PATH)
            target_table.alias("target").merge(
                batch_df.alias("source"),
                "target.tai_khoan = source.tai_khoan"
            ).whenMatchedUpdate(set={
                "so_gd_24h": col("source.so_gd_24h"),
                "tong_tien_24h": col("source.tong_tien_24h"),
                "lan_gd_gan_nhat": col("source.lan_gd_gan_nhat"),
                "cap_nhat_luc": col("source.cap_nhat_luc")
            }).whenNotMatchedInsert(values={
                "tai_khoan": col("source.tai_khoan"),
                "so_gd_24h": col("source.so_gd_24h"),
                "tong_tien_24h": col("source.tong_tien_24h"),
                "lan_gd_gan_nhat": col("source.lan_gd_gan_nhat"),
                "cap_nhat_luc": col("source.cap_nhat_luc")
            }).execute()
        else:
            batch_df.write \
                .format("delta") \
                .mode("overwrite") \
                .option("mergeSchema", "true") \
                .save(SILVER_TABLE_PATH)

    query = aggregated_df.writeStream \
        .outputMode("complete") \
        .foreachBatch(write_complete_batch) \
        .option("checkpointLocation", CHECKPOINT_PATH) \
        .start()

    query.awaitTermination()

if __name__ == "__main__":
    main()