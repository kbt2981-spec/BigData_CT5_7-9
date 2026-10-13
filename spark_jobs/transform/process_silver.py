import os
import sys
import time # Dùng để sleep

# 1. Đặt cấu hình môi trường
os.environ['JAVA_HOME'] = r'D:\Homework\Java\OpenJDK17U-jdk_x64_windows_hotspot_17.0.20.1_1\jdk-17.0.20.1+1'
os.environ['HADOOP_HOME'] = r'D:\Homework\Hadoop'
os.environ['PATH'] = os.environ['HADOOP_HOME'] + r'\bin;' + os.environ['PATH']
os.environ['PYSPARK_PYTHON'] = sys.executable
os.environ['PYSPARK_DRIVER_PYTHON'] = sys.executable

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_unixtime, to_timestamp
from delta.tables import DeltaTable # Dùng để kiểm tra bảng Delta

def main():
    # 2. Khởi tạo SparkSession
    spark = SparkSession.builder \
        .appName("BronzeToSilverETL") \
        .master("local[*]") \
        .config("spark.driver.memory", "1g") \
        .config("spark.executor.memory", "1g") \
        .config("spark.sql.shuffle.partitions", "2") \
        .config("spark.jars.packages", "io.delta:delta-spark_2.12:3.1.0") \
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
        .getOrCreate()

    spark.sparkContext.setLogLevel("WARN")

    # Bypass kiểm tra filesystem native
    spark.sparkContext._jsc.hadoopConfiguration().set("fs.file.impl", "org.apache.hadoop.fs.LocalFileSystem")
    spark.sparkContext._jsc.hadoopConfiguration().setBoolean("hadoop.native.lib", False)

    bronze_path = "./delta_lake/bronze/giao_dich"
    silver_path = "./delta_lake/silver/giao_dich"

    print("=== BẮT ĐẦU QUY TRÌNH ETL: BRONZE -> SILVER ===")

    # Vòng lặp chờ tầng Bronze sẵn sàng
    print(f"1. Đang kiểm tra đường dẫn Bronze: {bronze_path}")
    while not DeltaTable.isDeltaTable(spark, bronze_path):
        print("[!] Tầng Bronze chưa sẵn sàng (chưa có dữ liệu). Đang chờ 5 giây...")
        time.sleep(5)
    print("[*] Đã tìm thấy Delta Table hợp lệ ở Bronze. Bắt đầu đọc...")

    # 3. Đọc dữ liệu từ tầng Bronze
    bronze_df = spark.read.format("delta").load(bronze_path)
    initial_count = bronze_df.count()
    print(f"    -> Số lượng dòng ban đầu: {initial_count}")

    # 4. Làm sạch dữ liệu (Data Cleaning & Transformation) - Dùng tên cột tiếng Việt
    print("2. Đang thực hiện làm sạch dữ liệu...")
    
    # - Loại bỏ trùng lặp
    cleaned_df = bronze_df.dropDuplicates()

    # - Lọc bỏ bản ghi NULL ở các cột quan trọng (Sử dụng tên cột tiếng Việt)
    cleaned_df = cleaned_df.dropna(subset=["so_tien", "thoi_diem", "tai_khoan_nguon"])

    # - Lọc các giao dịch hợp lệ (so_tien >= 0)
    cleaned_df = cleaned_df.filter(col("so_tien") >= 0)

    # - Chuyển đổi thoi_gian_su_kien sang dạng TimestampReadable
    cleaned_df = cleaned_df.withColumn("thoi_gian_datetime", col("thoi_diem").cast("timestamp"))

    final_count = cleaned_df.count()
    print(f"    -> Số lượng dòng sau khi làm sạch: {final_count}")
    print(f"    -> Số dòng bị loại bỏ (trùng/lỗi): {initial_count - final_count}")

    # 5. Ghi dữ liệu đã làm sạch vào tầng Silver
    print(f"3. Đang ghi dữ liệu vào Silver Delta Lake tại: {silver_path}")
    cleaned_df.write \
        .format("delta") \
        .mode("overwrite") \
        .save(silver_path)

    print("=== HOÀN THÀNH QUY TRÌNH BRONZE -> SILVER ===")
    
    # Hiển thị thử 5 dòng đầu tiên tầng Silver (Đã loại bỏ cột "nhan" không tồn tại)
    print("\nMẫu dữ liệu tầng Silver:")
    cleaned_df.select("thoi_diem", "so_tien", "thoi_gian_datetime").show(5, truncate=False)

if __name__ == "__main__":
    main()