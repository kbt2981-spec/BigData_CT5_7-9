import os
import sys
import time

# 1. Đặt cấu hình môi trường
os.environ['JAVA_HOME'] = r'D:\Homework\Java\OpenJDK17U-jdk_x64_windows_hotspot_17.0.20.1_1\jdk-17.0.20.1+1'
os.environ['HADOOP_HOME'] = r'D:\Homework\Hadoop'
os.environ['PATH'] = os.environ['HADOOP_HOME'] + r'\bin;' + os.environ['PATH']
os.environ['PYSPARK_PYTHON'] = sys.executable
os.environ['PYSPARK_DRIVER_PYTHON'] = sys.executable

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, sum, round, avg
from delta.tables import DeltaTable

def main():
    # 2. Khởi tạo SparkSession
    spark = SparkSession.builder \
        .appName("SilverToGoldETL") \
        .master("local[*]") \
        .config("spark.driver.memory", "1g") \
        .config("spark.executor.memory", "1g") \
        .config("spark.sql.shuffle.partitions", "2") \
        .config("spark.jars.packages", "io.delta:delta-spark_2.12:3.1.0") \
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
        .getOrCreate()

    spark.sparkContext.setLogLevel("WARN")

    spark.sparkContext._jsc.hadoopConfiguration().set("fs.file.impl", "org.apache.hadoop.fs.LocalFileSystem")
    spark.sparkContext._jsc.hadoopConfiguration().setBoolean("hadoop.native.lib", False)

    silver_path = "./delta_lake/silver/giao_dich"
    gold_path = "./delta_lake/gold/thong_ke_giao_dich"

    print("=== BẮT ĐẦU QUY TRÌNH ETL: SILVER -> GOLD ===")

    # Vòng lặp chờ tầng Silver sẵn sàng
    print(f"1. Đang kiểm tra đường dẫn Silver: {silver_path}")
    while not DeltaTable.isDeltaTable(spark, silver_path):
        print("[!] Tầng Silver chưa sẵn sàng. Đang chờ 5 giây...")
        time.sleep(5)
    print("[*] Đã tìm thấy Delta Table hợp lệ ở Silver. Bắt đầu đọc...")

    # 3. Đọc dữ liệu từ tầng Silver
    silver_df = spark.read.format("delta").load(silver_path)
    
    print("2. Đang tính toán thống kê bảng Gold...")
    
    # Ví dụ: Thống kê tổng hợp giao dịch theo loại giao dịch ("loai") hoặc kênh ("kenh")
    # Thay vì dùng cột "nhan" gây lỗi, ta dùng cột "loai" có sẵn trong dữ liệu
    gold_df = silver_df.groupBy("loai").agg(
        count("*").alias("Tong_So_Giao_Dich"),
        round(sum("so_tien"), 2).alias("Tong_So_Tien"),
        round(avg("so_tien"), 2).alias("So_Tien_Trung_Binh")
    )

    print("3. Đang ghi dữ liệu vào Gold Delta Lake...")
    gold_df.write \
        .format("delta") \
        .mode("overwrite") \
        .save(gold_path)

    print("=== HOÀN THÀNH QUY TRÌNH SILVER -> GOLD ===")
    
    # Hiển thị mẫu kết quả tầng Gold
    print("\nMẫu dữ liệu tầng Gold:")
    gold_df.show(5, truncate=False)

if __name__ == "__main__":
    main()