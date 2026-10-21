import os
import sys
import json
from pathlib import Path

# Dam bao moi truong Java va Python hoat dong on dinh cho Spark Streaming tren Windows
os.environ["JAVA_HOME"] = r"D:\Homework\Java\OpenJDK17U-jdk_x64_windows_hotspot_17.0.20.1_1\jdk-17.0.20.1+1"
os.environ["HADOOP_HOME"] = r"D:\Homework\Hadoop"
os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

from pyspark.sql import SparkSession
from pyspark.ml import PipelineModel
from pyspark.ml.util import DefaultParamsReader
from pyspark.ml.functions import vector_to_array
from pyspark.sql.functions import col, lit, current_timestamp, array, struct, when, from_json, date_format
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, LongType
from delta import configure_spark_with_delta_pip

# --- MONKEY-PATCH: DOC METADATA TRUC TIEP BANG PYTHON THUAN TRANH SAP WORKER TREN WINDOWS ---
original_load_metadata = DefaultParamsReader.loadMetadata

def custom_load_metadata(path, sc, expectedClassName=""):
    try:
        clean_path = str(path).replace("file:///", "").replace("file://", "")
        metadata_dir = os.path.join(clean_path, "metadata")
        if os.path.exists(metadata_dir):
            files = [f for f in os.listdir(metadata_dir) if f.startswith("part-") or f.endswith(".json")]
            if files:
                file_path = os.path.join(metadata_dir, files[0])
                with open(file_path, "r", encoding="utf-8") as f:
                    return json.loads(f.readline())
    except Exception as ex:
        print(f"--> Custom metadata loader fallback: {ex}")
    return original_load_metadata(path, sc, expectedClassName)

DefaultParamsReader.loadMetadata = staticmethod(custom_load_metadata)
# -----------------------------------------------------------------------------------------

# 1. Khoi tao Spark Session voi Delta Lake extension
builder = SparkSession.builder \
    .appName("RealtimeScoring_FraudDetection") \
    .master("local[*]") \
    .config("spark.driver.host", "127.0.0.1") \
    .config("spark.pyspark.python", sys.executable) \
    .config("spark.pyspark.driver.python", sys.executable) \
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
    .config("spark.driver.memory", "2g")

spark = configure_spark_with_delta_pip(builder).getOrCreate()
spark.sparkContext.setLogLevel("WARN")

sc = spark.sparkContext
conf = sc._jsc.hadoopConfiguration()
conf.set("fs.file.impl", "org.apache.hadoop.fs.LocalFileSystem")
conf.setBoolean("hadoop.native.lib", False)

# 2. Xu ly duong dan
BASE_DIR = Path(r"D:\Homework\BigData_CT5_7-9")
abs_model_path = BASE_DIR / "models" / "gbt_fraud_model"

if not abs_model_path.exists():
    raise FileNotFoundError(f"Khong tim thay mo hinh tai {abs_model_path}.")

MODEL_PATH = abs_model_path.as_posix()
BRONZE_TABLE_PATH = (BASE_DIR / "delta_lake" / "bronze" / "giao_dich").as_posix()
CHECKPOINT_PATH = (BASE_DIR / "delta_lake" / "_checkpoints" / "gold_diem_rui_ro").as_posix()
GOLD_TABLE_PATH = (BASE_DIR / "delta_lake" / "gold" / "diem_rui_ro").as_posix()
MODEL_VERSION = "gbt_v1.0"

# 3. Load Model GBT
try:
    print(f"--> Loading GBT Pipeline Model from path: {MODEL_PATH}...")
    model = PipelineModel.load(MODEL_PATH)
    print("--> Tai mo hinh thanh cong!")
except Exception as e:
    print(f"\nLoi khi load mo hinh: {e}")
    raise e

# Dinh nghia Schema de parse JSON tu Bronze
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

# 4. Doc luong tu Bronze va Parse JSON
df_raw = spark.readStream \
    .format("delta") \
    .load(BRONZE_TABLE_PATH)

df_stream = df_raw \
    .withColumn("parsed_json", from_json(col("json_value"), schema)) \
    .select("parsed_json.*", "thoi_diem_nhan") \
    .withColumn("thoi_diem_ts", col("thoi_diem").cast("timestamp")) \
    .withWatermark("thoi_diem_ts", "1 minute")

# 5. Ham xu ly cham diem theo từng Micro-Batch
def process_micro_batch(batch_df, batch_id):
    if batch_df.isEmpty():
        return
    
    # Bo sung dac trung can thiet cho model GBT
    df_with_features = batch_df \
        .withColumn("so_gd_truoc_do", lit(0).cast("long")) \
        .withColumn("tong_tien_truoc_do", lit(0.0).cast("double")) \
        .withColumn("so_tien_gd_gan_nhat", lit(0.0).cast("double")) \
        .withColumn("sai_lech_so_du_nguon", col("newbalanceOrig") + col("so_tien") - col("oldbalanceOrg")) \
        .withColumn("sai_lech_so_du_dich", col("oldbalanceDest") + col("so_tien") - col("newbalanceDest")) \
        .withColumn("ty_le_so_tien_so_du_nguon", when(col("oldbalanceOrg") > 0, col("so_tien") / col("oldbalanceOrg")).otherwise(lit(1.0)))

    predictions = model.transform(df_with_features)

    processed_scores = predictions \
        .withColumn("prob_array", vector_to_array(col("probability"))) \
        .withColumn("diem_rui_ro", col("prob_array")[1]) \
        .withColumn("phien_ban_mo_hinh", lit(MODEL_VERSION)) \
        .withColumn("trang_thai_tham_dinh", lit("CHO_THAM_DINH")) \
        .withColumn("xep_hang_trong_ngay", lit(0).cast("int")) \
        .withColumn("do_tre_ms", (current_timestamp().cast("long") - col("thoi_diem_nhan").cast("long")) * 1000) \
        .withColumn("cac_yeu_to_chinh", array(
            struct(
                when(col("so_tien") > 10000000, lit("SO_TIEN_LON")).otherwise(lit("SO_TIEN_BINH_THUONG")).alias("ten"),
                when(col("so_tien") > 10000000, lit(0.6)).otherwise(lit(0.1)).alias("dong_gop")
            )
        )) \
        .select(
            "ma_giao_dich",
            "diem_rui_ro",
            "xep_hang_trong_ngay",
            "cac_yeu_to_chinh",
            "phien_ban_mo_hinh",
            "do_tre_ms",
            "trang_thai_tham_dinh",
            col("thoi_diem").cast("string").alias("thoi_diem")  # Ep kieu ve string de dong nhat schema Gold
        )

    processed_scores.write \
        .format("delta") \
        .mode("append") \
        .option("mergeSchema", "true") \
        .save(GOLD_TABLE_PATH)

# 6. Thuc thi luong Structured Streaming
query = df_stream.writeStream \
    .foreachBatch(process_micro_batch) \
    .option("checkpointLocation", CHECKPOINT_PATH) \
    .start()

query.awaitTermination()