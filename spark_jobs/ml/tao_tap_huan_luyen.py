import os
import sys

# Cau hinh moi truong Java & Hadoop tren Windows
JAVA_HOME = r"D:\Homework\Java\OpenJDK17U-jdk_x64_windows_hotspot_17.0.20.1_1\jdk-17.0.20.1+1"
HADOOP_HOME = r"D:\Homework\Hadoop"

os.environ["JAVA_HOME"] = JAVA_HOME
os.environ["HADOOP_HOME"] = HADOOP_HOME
os.environ["PATH"] = (
    os.path.join(JAVA_HOME, "bin") + os.pathsep +
    os.path.join(HADOOP_HOME, "bin") + os.pathsep +
    os.environ.get("PATH", "")
)
os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, when, coalesce, lit, count, sum as spark_sum,
    lag, to_timestamp, current_timestamp
)
from pyspark.sql.window import Window
from delta import configure_spark_with_delta_pip

def main():
    print("=== [1] KHOI TAO POINT-IN-TIME FEATURE STORE (CHONG DATA LEAKAGE) ===")
    builder = SparkSession.builder \
        .appName("PointInTimeFeatureStore") \
        .master("local[*]") \
        .config("spark.driver.memory", "4g") \
        .config("spark.executor.memory", "4g") \
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")

    spark = configure_spark_with_delta_pip(builder).getOrCreate()
    spark.sparkContext.setLogLevel("WARN")

    PROJECT_DIR = r"D:\Homework\BigData_CT5_7-9"
    silver_path = os.path.join(PROJECT_DIR, "delta_lake", "silver", "giao_dich").replace("\\", "/")
    tham_dinh_path = os.path.join(PROJECT_DIR, "delta_lake", "silver", "ket_luan_tham_dinh").replace("\\", "/")
    features_path = os.path.join(PROJECT_DIR, "delta_lake", "features", "tap_huan_luyen").replace("\\", "/")

    print(f"--> Doc du lieu tu Silver: {silver_path}")
    if not os.path.exists(silver_path):
        print(f"[!] Khong tim thay du lieu Silver tai {silver_path}. Ket thuc.")
        return

    df = spark.read.format("delta").load(silver_path)

    # 1. Chuan hoa timestamp va step de sap xep theo dong thoi gian
    if "thoi_gian_datetime" in df.columns:
        df = df.withColumn("ts", col("thoi_gian_datetime"))
    elif "thoi_diem" in df.columns:
        df = df.withColumn("ts", to_timestamp(col("thoi_diem")))
    else:
        df = df.withColumn("ts", col("step").cast("timestamp"))

    # 2. XAY DUNG POINT-IN-TIME WINDOW CHONG DATA LEAKAGE
    # RANG BUOC: Chi lay cac giao dich xay ra TRUOC thoi diem giao dich hien tai (rowsBetween unboundedPreceding -> -1)
    # Tuyet doi khong lay thong tin cua chinh giao dich hien tai hoac giao dich trong tuong lai.
    user_window = Window.partitionBy("tai_khoan_nguon").orderBy("step", "ts").rowsBetween(Window.unboundedPreceding, -1)

    print("--> Dang tinh toan dac trung lich su point-in-time...")
    df_features = df \
        .withColumn("so_gd_truoc_do", coalesce(count("ma_giao_dich").over(user_window), lit(0))) \
        .withColumn("tong_tien_truoc_do", coalesce(spark_sum("so_tien").over(user_window), lit(0.0))) \
        .withColumn("so_tien_gd_gan_nhat", coalesce(lag("so_tien", 1).over(Window.partitionBy("tai_khoan_nguon").orderBy("step", "ts")), lit(0.0)))

    # 3. Tinh toan dac trung ty le va sai lech so du
    df_features = df_features \
        .withColumn("sai_lech_so_du_nguon", col("newbalanceOrig") + col("so_tien") - col("oldbalanceOrg")) \
        .withColumn("sai_lech_so_du_dich", col("oldbalanceDest") + col("so_tien") - col("newbalanceDest")) \
        .withColumn("ty_le_so_tien_so_du_nguon", when(col("oldbalanceOrg") > 0, col("so_tien") / col("oldbalanceOrg")).otherwise(lit(1.0)))

    # 4. TICH HOP VONG PHAN HOI NHAN (FEEDBACK LOOP TU THAM DINH VIEN)
    # Neu co bang ket luan tham dinh thi cap nhat nhan isFraud moi nhat
    if os.path.exists(tham_dinh_path):
        print(f"--> Tich hop nhan tu tham dinh vien tai: {tham_dinh_path}")
        try:
            df_feedback = spark.read.format("delta").load(tham_dinh_path)
            # Ket luan 'GIAN_LAN' -> 1.0, 'HOP_LE' -> 0.0
            df_feedback = df_feedback.withColumn(
                "nhan_moi",
                when(col("ket_luan") == "GIAN_LAN", lit(1.0))
                .when(col("ket_luan") == "HOP_LE", lit(0.0))
                .otherwise(lit(None))
            ).select("ma_giao_dich", "nhan_moi")

            df_features = df_features.join(df_feedback, on="ma_giao_dich", how="left")
            df_features = df_features.withColumn(
                "isFraud",
                coalesce(col("nhan_moi"), col("isFraud"))
            ).drop("nhan_moi")
            print("--> Da tich hop thanh cong nhan tu tham dinh vien.")
        except Exception as e:
            print(f"[!] Chua doc duoc Delta feedback: {e}, giu nguyen nhan isFraud goc.")

    # 5. Ghi vao bang Delta Features (features.tap_huan_luyen)
    print(f"--> Dang luu bang dac trung tai: {features_path}")
    df_features.write \
        .format("delta") \
        .mode("overwrite") \
        .option("overwriteSchema", "true") \
        .save(features_path)

    print("=== HOAN TAT TAO TAP HUAN LUYEN POINT-IN-TIME THANH CONG! ===")
    df_features.select("step", "ma_giao_dich", "tai_khoan_nguon", "so_tien", "so_gd_truoc_do", "tong_tien_truoc_do", "isFraud").show(5)

if __name__ == "__main__":
    main()
