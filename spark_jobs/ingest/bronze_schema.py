from pyspark.sql.types import StructType, StructField, StringType, DoubleType, TimestampType, DateType, IntegerType
from pyspark.sql.functions import col, to_date

bronze_schema = StructType([
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
    StructField("kenh", StringType(), True),
    StructField("isFraud_Goc", IntegerType(), True)
])