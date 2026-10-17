import os
import sys
import time # Dung de sleep

# 1. Dat cau hinh moi truong
os.environ['JAVA_HOME'] = r'D:\Homework\Java\OpenJDK17U-jdk_x64_windows_hotspot_17.0.20.1_1\jdk-17.0.20.1+1'
os.environ['HADOOP_HOME'] = r'D:\Homework\Hadoop'
os.environ['PATH'] = os.environ['HADOOP_HOME'] + r'\bin;' + os.environ['PATH']
os.environ['PYSPARK_PYTHON'] = sys.executable
os.environ['PYSPARK_DRIVER_PYTHON'] = sys.executable

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, to_timestamp
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, LongType
from delta.tables import DeltaTable # Dung de kiem tra bang Delta

def main():
    # 2. Khoi tao SparkSession kem cau hinh nang cap bo nho Heap len 4g de chong tran RAM (OutOfMemoryError)
    spark = SparkSession.builder \
        .appName("BronzeToSilverETL") \
        .master("local[*]") \
        .config("spark.driver.memory", "4g") \
        .config("spark.executor.memory", "4g") \
        .config("spark.sql.shuffle.partitions", "200") \
        .config("spark.driver.maxResultSize", "2g") \
        .config("spark.jars.packages", "io.delta:delta-spark_2.12:3.1.0") \
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
        .getOrCreate()

    spark.sparkContext.setLogLevel("WARN")

    # Bypass kiem tra filesystem native
    spark.sparkContext._jsc.hadoopConfiguration().set("fs.file.impl", "org.apache.hadoop.fs.LocalFileSystem")
    spark.sparkContext._jsc.hadoopConfiguration().setBoolean("hadoop.native.lib", False)

    bronze_path = "./delta_lake/bronze/giao_dich"
    silver_path = "./delta_lake/silver/giao_dich"

    print("=== BAT DAU QUY TRINH ETL: BRONZE -> SILVER ===")

    # Vong lap cho tang Bronze san sang
    print(f"1. Dang kiem tra duong dan Bronze: {bronze_path}")
    while not DeltaTable.isDeltaTable(spark, bronze_path):
        print("[!] Tang Bronze chua san sang (chua co du lieu). Dang cho 5 giay...")
        time.sleep(5)
    print("[*] Da tim thay Delta Table hop le o Bronze. Bat dau doc...")

    # 3. Doc du lieu tho tu tang Bronze (dang JSON string)
    bronze_df = spark.read.format("delta").load(bronze_path)
    initial_count = bronze_df.count()
    print(f"    -> So luong dong ban dau: {initial_count}")

    # Dinh nghia Schema cho du lieu PaySim de parse JSON
    schema = StructType([
        StructField("step", LongType(), True),
        StructField("type", StringType(), True),
        StructField("so_tien", DoubleType(), True),
        StructField("tai_khoan_nguon", StringType(), True),
        StructField("oldbalanceOrg", DoubleType(), True),
        StructField("newbalanceOrig", DoubleType(), True),
        StructField("tai_khoan_dich", StringType(), True),
        StructField("oldbalanceDest", DoubleType(), True),
        StructField("newbalanceDest", DoubleType(), True),
        StructField("isFraud", LongType(), True),
        StructField("thoi_diem", StringType(), True),
        StructField("ma_giao_dich", StringType(), True)
    ])

    # Parse chuoi JSON tu cot json_value thanh cac truong du lieu cu the
    parsed_df = bronze_df.withColumn("parsed_json", from_json(col("json_value"), schema)) \
                         .select("parsed_json.*", "thoi_diem_nhan")

    # 4. Lam sach du lieu (Data Cleaning & Transformation)
    print("2. Dang thuc hien lam sach du lieu...")
    
    # - Loai bo trung lap
    cleaned_df = parsed_df.dropDuplicates()

    # - Loc bo ban ghi NULL o cac cot quan trong
    cleaned_df = cleaned_df.dropna(subset=["so_tien", "thoi_diem", "tai_khoan_nguon", "ma_giao_dich"])

    # - Loc cac giao dich hop le (so_tien >= 0)
    cleaned_df = cleaned_df.filter(col("so_tien") >= 0)

    # - Chuyen doi thoi_diem sang dang Timestamp
    cleaned_df = cleaned_df.withColumn("thoi_gian_datetime", col("thoi_diem").cast("timestamp"))

    final_count = cleaned_df.count()
    print(f"    -> So luong dong sau khi lam sach: {final_count}")
    print(f"    -> So dong bi loai bo (trung/loi): {initial_count - final_count}")

    # 5. Ghi du lieu da lam sach vao tang Silver
    print(f"3. Dang ghi du lieu vao Silver Delta Lake tai: {silver_path}")
    cleaned_df.write \
        .format("delta") \
        .mode("overwrite") \
        .save(silver_path)

    print("=== HOAN THANH QUY TRINH BRONZE -> SILVER ===")
    
    # Hien thi thu 5 dong dau tien tang Silver
    print("\nMau du lieu tang Silver:")
    cleaned_df.select("thoi_diem", "ma_giao_dich", "so_tien", "tai_khoan_nguon").show(5, truncate=False)

if __name__ == "__main__":
    main()