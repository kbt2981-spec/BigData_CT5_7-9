from pyspark.sql import SparkSession
from delta import configure_spark_with_delta_pip
import os

# Khởi tạo SparkSession tương tự backend
builder = SparkSession.builder \
    .appName("SeedMockData") \
    .master("local[*]") \
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")

spark = configure_spark_with_delta_pip(builder).getOrCreate()

# Dữ liệu mẫu giao dịch gian lận giả lập từ PaySim
mock_data = [
    ("TXN_882910", 14, "TRANSFER", 250000.0, 0.95, "2026-10-16 12:00:00", "CHUA_XU_LY"),
    ("TXN_882911", 14, "CASH_OUT", 180000.0, 0.88, "2026-10-16 12:05:00", "CHUA_XU_LY"),
    ("TXN_882912", 15, "TRANSFER", 500000.0, 0.92, "2026-10-16 12:10:00", "CHUA_XU_LY")
]
columns = ["ma_giao_dich", "step", "type", "amount", "diem_rui_ro", "thoi_gian", "ket_luan"]

df = spark.createDataFrame(mock_data, columns)

# Ghi vào bảng Delta Lake Gold
gold_path = "./delta_lake/gold/diem_rui_ro"
df.write.format("delta").mode("overwrite").save(gold_path)
print("Đã tạo dữ liệu mẫu vào Delta Lake thành công!")