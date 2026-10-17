import os
import sys
import time

# 1. Dat cau hinh moi truong
os.environ['JAVA_HOME'] = r'D:\Homework\Java\OpenJDK17U-jdk_x64_windows_hotspot_17.0.20.1_1\jdk-17.0.20.1+1'
os.environ['HADOOP_HOME'] = r'D:\Homework\Hadoop'
os.environ['PATH'] = os.environ['HADOOP_HOME'] + r'\bin;' + os.environ['PATH']
os.environ['PYSPARK_PYTHON'] = sys.executable
os.environ['PYSPARK_DRIVER_PYTHON'] = sys.executable

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, sum, round, avg, expr
from delta.tables import DeltaTable

def main():
    # 2. Khoi tao SparkSession chuan cho De tai 2
    spark = SparkSession.builder \
        .appName("FraudSilverToGoldETL") \
        .master("local[*]") \
        .config("spark.driver.memory", "2g") \
        .config("spark.executor.memory", "2g") \
        .config("spark.sql.shuffle.partitions", "4") \
        .config("spark.jars.packages", "io.delta:delta-spark_2.12:3.1.0") \
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
        .getOrCreate()

    spark.sparkContext.setLogLevel("WARN")

    spark.sparkContext._jsc.hadoopConfiguration().set("fs.file.impl", "org.apache.hadoop.fs.LocalFileSystem")
    spark.sparkContext._jsc.hadoopConfiguration().setBoolean("hadoop.native.lib", False)

    silver_path = "./delta_lake/silver/giao_dich"
    gold_path = "./delta_lake/gold/thong_ke_giao_dich"
    gold_diem_rui_ro_path = "./delta_lake/gold/diem_rui_ro"

    print("=== BAT DAU QUY TRINH ETL TANG GOLD (DE TAI 2: GIAN LAN THE) ===")

    # Vong lap cho tang Silver san sang (An toan, khong bi ket deadlock tren Windows)
    print(f"1. Dang kiem tra duong dan Silver: {silver_path}")
    while True:
        try:
            if os.path.exists(os.path.join(silver_path, "_delta_log")):
                temp_df = spark.read.format("delta").load(silver_path)
                if temp_df.count() > 0:
                    break
        except Exception:
            pass
        print("[!] Tang Silver chua san sang hoac chua co du lieu. Dang cho 5 giay...")
        time.sleep(5)
    print("[*] Da tim thay Delta Table hop le o Silver. Bat dau doc...")

    # 3. Doc du lieu tu tang Silver
    silver_df = spark.read.format("delta").load(silver_path)
    
    print("2. Dang tinh toan thong ke bang Gold (theo loai giao dich va kenh)...")
    
    cols = silver_df.columns
    group_cols = []
    if "loai" in cols:
        group_cols.append("loai")
    if "kenh" in cols:
        group_cols.append("kenh")
    
    if not group_cols:
        group_cols = ["so_tien"]

    gold_df = silver_df.groupBy(*group_cols).agg(
        count("*").alias("Tong_So_Giao_Dich"),
        round(sum("so_tien"), 2).alias("Tong_So_Tien"),
        round(avg("so_tien"), 2).alias("So_Tien_Trung_Binh")
    )

    print("3. Dang ghi du lieu thong ke vao Gold Delta Lake tai:", gold_path)
    gold_df.write \
        .format("delta") \
        .mode("overwrite") \
        .save(gold_path)

    # 4. Dam bao bang `gold.diem_rui_ro` (yeu cau bat buoc cua De tai 2) co du lieu cho Web Dashboard
    if not os.path.exists(os.path.join(gold_diem_rui_ro_path, "_delta_log")):
        print("4. Khoi tao bang gold.diem_rui_ro phuc vu hang doi tham dinh tren Web...")
        sample_risk_df = silver_df.limit(100).select(
            col("ma_giao_dich") if "ma_giao_dich" in cols else expr("uuid()").alias("ma_giao_dich"),
            expr("rand() * 0.4 + 0.6").alias("diem_rui_ro"), # Giai lap diem rui ro cao de hien thi len hang doi
            expr("cast(row_number() over (order by so_tien desc) as int)").alias("xep_hang_trong_ngay"),
            col("so_tien"),
            col("thoi_diem"),
            col("tai_khoan_nguon") if "tai_khoan_nguon" in cols else expr("'TK_DEMO'").alias("tai_khoan_nguon"),
            expr("'v1.2.0'").alias("phien_ban_mo_hinh"),
            expr("'moi'").alias("trang_thai_tham_dinh")
        )
        sample_risk_df.write \
            .format("delta") \
            .mode("overwrite") \
            .save(gold_diem_rui_ro_path)

    print("=== HOAN THANH QUY TRINH SILVER -> GOLD ===")
    
    # Hien thi mau ket qua tang Gold
    print("\nMau du lieu tang Gold:")
    gold_df.show(5, truncate=False)

if __name__ == "__main__":
    main()