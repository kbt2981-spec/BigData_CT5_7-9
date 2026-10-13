import os
from pyspark.ml import PipelineModel
from pyspark.ml.functions import vector_to_array
from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    array,
    col,
    current_timestamp,
    lit,
    struct,
    unix_timestamp,
    when,
)

# 1. Khởi tạo Spark Session với Delta Lake extension
spark = (
    SparkSession.builder.appName("RealtimeScoring_FraudDetection")
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
    .config(
        "spark.sql.catalog.spark_catalog",
        "org.apache.spark.sql.delta.catalog.DeltaCatalog",
    )
    .getOrCreate()
)

# 2. Cấu hình đường dẫn chuẩn xác (Khắc phục lỗi lặp thư mục)
BASE_DIR = r"D:\Homework\BigData_CT5_7-9"
MODEL_PATH = os.path.join(BASE_DIR, "models", "gbt_fraud_model").replace(
    "\\", "/"
)
CHECKPOINT_PATH = os.path.join(
    BASE_DIR, "delta_lake", "_checkpoints", "gold_diem_rui_ro"
).replace("\\", "/")
MODEL_VERSION = "gbt_v1.0"

# 3. Load Model GBT đã huấn luyện từ thư mục cục bộ
print(f"--> Loading GBT Model from: {MODEL_PATH}...")
model = PipelineModel.load(MODEL_PATH)

# 4. Đọc luồng dữ liệu giao dịch từ Bronze kèm Watermark (1 phút)
df_stream = (
    spark.readStream.format("delta")
    .table("bronze.giao_dich")
    .withWatermark("thoi_diem", "1 minute")
)


# 5. Hàm xử lý chấm điểm theo từng Micro-Batch
def process_micro_batch(batch_df, batch_id):
  if batch_df.isEmpty():
    return

  # Đọc trạng thái khách hàng hiện tại từ bảng Silver
  df_silver_state = spark.read.table("silver.trang_thai_khach_hang")

  # Stream-Static Join: Join theo khóa tài khoản nguồn
  df_joined = batch_df.join(
      df_silver_state,
      batch_df["tai_khoan_nguon"] == df_silver_state["tai_khoan"],
      "left",
  ).na.fill(0)

  # Chạy mô hình dự báo (Inference)
  predictions = model.transform(df_joined)

  # Chuyển đổi và định dạng dữ liệu khớp đúng đặc tả schema gold.diem_rui_ro
  processed_scores = (
      predictions.withColumn("prob_array", vector_to_array(col("probability")))
      .withColumn("diem_rui_ro", col("prob_array")[1])
      .withColumn("phien_ban_mo_hinh", lit(MODEL_VERSION))
      .withColumn("trang_thai_tham_dinh", lit("CHO_THAM_DINH"))
      .withColumn("xep_hang_trong_ngay", lit(0).cast("int"))
      .withColumn(
          "do_tre_ms",
          (current_timestamp().cast("long") - col("thoi_diem_nhan").cast("long"))
          * 1000,
      )
      .withColumn(
          "cac_yeu_to_chinh",
          array(
              struct(
                  when(
                      col("so_tien") > 10000000, lit("SO_TIEN_LON")
                  )
                  .otherwise(lit("SO_TIEN_BINH_THUONG"))
                  .alias("ten"),
                  when(col("so_tien") > 10000000, lit(0.6))
                  .otherwise(lit(0.1))
                  .alias("dong_gop"),
              )
          ),
      )
      .select(
          "ma_giao_dich",
          "diem_rui_ro",
          "xep_hang_trong_ngay",
          "cac_yeu_to_chinh",
          "phien_ban_mo_hinh",
          "do_tre_ms",
          "trang_thai_tham_dinh",
      )
  )

  # Ghi dữ liệu chấm điểm rủi ro vào bảng Gold
  processed_scores.write.format("delta").mode("append").saveAsTable(
      "gold.diem_rui_ro"
  )


# 6. Thực thi luồng Structured Streaming với foreachBatch
query = (
    df_stream.writeStream.foreachBatch(process_micro_batch)
    .option("checkpointLocation", CHECKPOINT_PATH)
    .start()
)

query.awaitTermination()