import os
import sys

os.environ['JAVA_HOME'] = r'D:\Homework\Java\OpenJDK17U-jdk_x64_windows_hotspot_17.0.20.1_1\jdk-17.0.20.1+1'
os.environ['HADOOP_HOME'] = r'D:\Homework\Hadoop'
os.environ['PYSPARK_PYTHON'] = sys.executable
os.environ['PYSPARK_DRIVER_PYTHON'] = sys.executable

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, to_date
from pyspark.sql.types import StructType, StructField, DoubleType, StringType, TimestampType

def main():
    spark = SparkSession.builder \
        .appName("KafkaToBronzeConsumer") \
        .master("local[*]") \
        .config("spark.driver.memory", "1g") \
        .config("spark.executor.memory", "1g") \
        .config("spark.sql.shuffle.partitions", "2") \
        .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,io.delta:delta-spark_2.12:3.1.0") \
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
        .getOrCreate()

    spark.sparkContext.setLogLevel("WARN")
    sc = spark.sparkContext
    conf = sc._jsc.hadoopConfiguration()
    conf.set("fs.file.impl", "org.apache.hadoop.fs.LocalFileSystem")

    # Schema chuẩn theo Đề tài 2 (Bảng bronze.giao_dich)
    schema = StructType([
        StructField("ma_giao_dich", StringType(), True),
        StructField("thoi_diem", TimestampType(), True),
        StructField("thoi_diem_nhan", TimestampType(), True),
        StructField("tai_khoan_nguon", StringType(), True),
        StructField("tai_khoan_dich", StringType(), True),
        StructField("loai", StringType(), True),
        StructField("so_tien", DoubleType(), True),
        StructField("so_du_truoc_nguon", DoubleType(), True),
        StructField("so_du_sau_nguon", DoubleType(), True),
        StructField("so_du_truoc_dich", DoubleType(), True),
        StructField("so_du_sau_dich", DoubleType(), True),
        StructField("kenh", StringType(), True)
    ])

    kafka_stream = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "localhost:9092") \
        .option("subscribe", "transactions") \
        .option("startingOffsets", "earliest") \
        .load()

    # Parse JSON và tự động tạo cột 'ngay' để phân vùng
    parsed_stream = kafka_stream.select(
        from_json(col("value").cast(StringType()), schema).alias("data")
    ).select("data.*") \
     .withColumn("ngay", to_date(col("thoi_diem")))

    bronze_table_path = "./delta_lake/bronze/giao_dich"
    checkpoint_path = "./delta_lake/bronze/checkpoint"

    # Bắt buộc partitionBy("ngay") theo yêu cầu kiến trúc
    query = parsed_stream.writeStream \
        .format("delta") \
        .outputMode("append") \
        .partitionBy("ngay") \
        .option("checkpointLocation", checkpoint_path) \
        .start(bronze_table_path)

    query.awaitTermination()

if __name__ == "__main__":
    main()