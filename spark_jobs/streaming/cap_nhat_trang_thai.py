import os
import sys

JAVA_HOME = r"D:\Homework\Java\OpenJDK17U-jdk_x64_windows_hotspot_17.0.20.1_1\jdk-17.0.20.1+1"
HADOOP_HOME = r"D:\Homework\Hadoop"

# --- TRÌNH KIỂM TRA ĐƯỜNG DẪN (Phát hiện lỗi ngay lập tức) ---
java_exe_path = os.path.join(JAVA_HOME, "bin", "java.exe")
winutils_path = os.path.join(HADOOP_HOME, "bin", "winutils.exe")

if not os.path.exists(java_exe_path):
    raise FileNotFoundError(f"\n[LỖI NGHIÊM TRỌNG]: Không tìm thấy java.exe tại {java_exe_path}\n=> Vui lòng mở File Explorer kiểm tra lại xem thư mục có bị lồng nhau không!")

if not os.path.exists(winutils_path):
    raise FileNotFoundError(f"\n[LỖI NGHIÊM TRỌNG]: Không tìm thấy winutils.exe tại {winutils_path}\n=> Vui lòng tải winutils và đặt vào thư mục bin của Hadoop!")
# -------------------------------------------------------------

# Cấu hình biến môi trường
os.environ["JAVA_HOME"] = JAVA_HOME
os.environ["HADOOP_HOME"] = HADOOP_HOME

java_bin = os.path.join(JAVA_HOME, "bin")
hadoop_bin = os.path.join(HADOOP_HOME, "bin")
os.environ["PATH"] = java_bin + os.path.pathsep + hadoop_bin + os.path.pathsep + os.environ.get("PATH", "")

# Cấu hình Python cho PySpark
venv_python = sys.executable 
os.environ["PYSPARK_PYTHON"] = venv_python
os.environ["PYSPARK_DRIVER_PYTHON"] = venv_python
sys.setrecursionlimit(15000)

from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, TimestampType, IntegerType

def update_state_func(key, pdf_iterator, state):
    import pandas as pd 
    tai_khoan = key[0]

    if state.hasTimedOut:
        state.remove()
        return

    # Khôi phục trạng thái cũ nếu đã tồn tại
    if state.exists:
        state_data = state.get()
        so_gd_24h = state_data[0]
        tong_tien_24h = state_data[1]
        lan_gd_gan_nhat = state_data[2]
    else:
        so_gd_24h = 0
        tong_tien_24h = 0.0
        lan_gd_gan_nhat = None

    max_event_time = lan_gd_gan_nhat

    # Duyệt qua các micro-batch dữ liệu đến trong state
    for pdf in pdf_iterator:
        if pdf.empty:
            continue
        so_gd_24h += len(pdf)
        tong_tien_24h += float(pdf["so_tien"].sum())
        
        if "thoi_diem" in pdf.columns and not pdf["thoi_diem"].empty:
            valid_times = pd.to_datetime(pdf["thoi_diem"]).dropna()
            if not valid_times.empty:
                batch_max_time = valid_times.max()
                if max_event_time is None or batch_max_time > max_event_time:
                    max_event_time = batch_max_time

    # Nếu không tìm thấy thời gian hợp lệ, giữ nguyên hoặc gán thời gian hiện tại
    if max_event_time is None:
        max_event_time = pd.Timestamp.now()

    # Cập nhật lại state
    state.update((so_gd_24h, tong_tien_24h, max_event_time))
    
    # Thiết lập thời gian timeout cho state (ví dụ: sau 30 ngày không có giao dịch thì xóa state)
    ts_millisecond = int(max_event_time.timestamp() * 1000) + (30 * 24 * 60 * 60 * 1000)
    state.setTimeoutTimestamp(ts_millisecond)

    result_pdf = pd.DataFrame([{
        "tai_khoan": tai_khoan,
        "so_gd_24h": so_gd_24h,
        "tong_tien_24h": tong_tien_24h,
        "lan_gd_gan_nhat": max_event_time,
        "cap_nhat_luc": pd.Timestamp.now()
    }])

    yield result_pdf

def main():
    spark = SparkSession.builder \
        .appName("FraudStateManagement") \
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
        .config("spark.jars.packages", "io.delta:delta-spark_2.12:3.2.0,org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0") \
        .getOrCreate()

    spark.sparkContext.setLogLevel("WARN")
    spark.sql("CREATE DATABASE IF NOT EXISTS silver")

    kafka_schema = StructType([
        StructField("tai_khoan_nguon", StringType(), True),
        StructField("so_tien", DoubleType(), True),
        StructField("thoi_diem", TimestampType(), True)
    ])

    state_schema = StructType([
        StructField("so_gd_24h", IntegerType(), True),
        StructField("tong_tien_24h", DoubleType(), True),
        StructField("lan_gd_gan_nhat", TimestampType(), True)
    ])

    output_schema = StructType([
        StructField("tai_khoan", StringType(), True),
        StructField("so_gd_24h", IntegerType(), True),
        StructField("tong_tien_24h", DoubleType(), True),
        StructField("lan_gd_gan_nhat", TimestampType(), True),
        StructField("cap_nhat_luc", TimestampType(), True)
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

    stateful_df = parsed_df \
        .withWatermark("thoi_diem", "10 minutes") \
        .groupBy("tai_khoan_nguon") \
        .applyInPandasWithState(
            func=update_state_func,
            outputStructType=output_schema,
            stateStructType=state_schema,
            outputMode="update",
            timeoutConf="EventTimeTimeout"
        )

    # ĐỊNH NGHĨA HÀM UPSERT TRƯỚC KHI GỌI writeStream
    def upsert_to_delta(micro_batch_df, batch_id):
        # Tránh lỗi timeout bằng cách dùng count() kiểm tra thay vì rdd.isEmpty()
        if micro_batch_df.count() == 0:
            return
            
        micro_batch_df.createOrReplaceTempView("updates")
        
        if not spark.catalog.tableExists("silver.trang_thai_khach_hang"):
            micro_batch_df.write.format("delta").mode("append").saveAsTable("silver.trang_thai_khach_hang")
            return

        spark.sql("""
            MERGE INTO silver.trang_thai_khach_hang target
            USING updates source
            ON target.tai_khoan = source.tai_khoan
            WHEN MATCHED THEN
                UPDATE SET 
                    target.so_gd_24h = source.so_gd_24h,
                    target.tong_tien_24h = source.tong_tien_24h,
                    target.lan_gd_gan_nhat = source.lan_gd_gan_nhat,
                    target.cap_nhat_luc = source.cap_nhat_luc
            WHEN NOT MATCHED THEN
                INSERT *
        """)

    query = stateful_df.writeStream \
        .outputMode("update") \
        .foreachBatch(upsert_to_delta) \
        .option("checkpointLocation", "./delta_lake/silver/checkpoint_state") \
        .start()

    query.awaitTermination()

if __name__ == "__main__":
    main()