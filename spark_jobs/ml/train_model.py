import os
import sys

# 1. Cấu hình môi trường Python, Java & Hadoop
os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

os.environ["JAVA_HOME"] = r"D:\Homework\Java\OpenJDK17U-jdk_x64_windows_hotspot_17.0.20.1_1\jdk-17.0.20.1+1"
os.environ["HADOOP_HOME"] = r"D:\Homework\Hadoop"
os.environ["PATH"] = (
    os.path.join(os.environ["JAVA_HOME"], "bin") + os.pathsep +
    os.path.join(os.environ["HADOOP_HOME"], "bin") + os.pathsep +
    os.environ.get("PATH", "")
)

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when, row_number
from pyspark.sql.window import Window
from pyspark.sql.types import NumericType, DoubleType
from pyspark.ml.feature import VectorAssembler, StandardScaler
from pyspark.ml.classification import GBTClassifier
from pyspark.ml.evaluation import BinaryClassificationEvaluator
from pyspark.ml import Pipeline
from pyspark.ml.functions import vector_to_array
from delta import configure_spark_with_delta_pip

# 2. Khởi tạo Spark Session tích hợp Delta Lake
builder = SparkSession.builder \
    .appName("TrainFraudDetectionModel") \
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")

spark = configure_spark_with_delta_pip(builder).getOrCreate()

# 3. Đọc dữ liệu từ Delta Lake Silver
print("--> Đang tải dữ liệu từ Delta Lake...")
SILVER_PATH = r"D:\Homework\BigData_CT5_7-9\delta_lake\silver\giao_dich"
df = spark.read.format("delta").load(SILVER_PATH)

# 4. Xác định cột nhãn & Ép kiểu dữ liệu về DoubleType
target_col = "Class" if "Class" in df.columns else "is_fraud"
df = df.withColumn(target_col, col(target_col).cast(DoubleType()))

# 5. Phân chia Stratified Split (Đảm bảo tập Test luôn nhận được mẫu gian lận)
fraud_df = df.filter(col(target_col) == 1.0)
normal_df = df.filter(col(target_col) == 0.0)

f_train, f_val, f_test = fraud_df.randomSplit([0.7, 0.15, 0.15], seed=42)
n_train, n_val, n_test = normal_df.randomSplit([0.7, 0.15, 0.15], seed=42)

train_df = f_train.union(n_train).cache()
val_df = f_val.union(n_val).cache()
test_df = f_test.union(n_test).cache()

total_rows = df.count()
train_pos = train_df.filter(col(target_col) == 1.0).count()
val_pos = val_df.filter(col(target_col) == 1.0).count()
test_pos = test_df.filter(col(target_col) == 1.0).count()

print(f"Tổng số bản ghi: {total_rows}")
print(f"-> Train: {train_df.count()} | Số gian lận (1): {train_pos}")
print(f"-> Val:   {val_df.count()} | Số gian lận (1): {val_pos}")
print(f"-> Test:  {test_df.count()} | Số gian lận (1): {test_pos}")

# 6. Xử lý mất cân bằng dữ liệu trên tập Train
num_pos = train_pos
num_neg = train_df.count() - num_pos
pos_weight = float(num_neg) / float(num_pos) if num_pos > 0 else 1.0

train_df = train_df.withColumn("weight", when(col(target_col) == 1.0, pos_weight).otherwise(1.0))

# 7. Lọc danh sách đặc trưng dạng số
exclude_cols = ["Class", "is_fraud", "row_id", "weight", "Time", "event_datetime"]
feature_cols = [
    field.name for field in df.schema.fields 
    if isinstance(field.dataType, NumericType) and field.name not in exclude_cols
]

print(f"--> Số lượng đặc trưng dạng số đưa vào mô hình: {len(feature_cols)}")

assembler = VectorAssembler(inputCols=feature_cols, outputCol="raw_features", handleInvalid="skip")
scaler = StandardScaler(inputCol="raw_features", outputCol="features", withStd=True, withMean=True)

# 8. Cấu hình & Huấn luyện GBTClassifier
gbt = GBTClassifier(
    labelCol=target_col, 
    featuresCol="features", 
    weightCol="weight",
    maxDepth=5, 
    maxIter=20, 
    seed=42
)

pipeline = Pipeline(stages=[assembler, scaler, gbt])

print("--> Đang huấn luyện mô hình GBTClassifier...")
model = pipeline.fit(train_df)

# 9. Dự đoán trên tập Test
predictions = model.transform(test_df)
predictions = predictions.withColumn("prob_array", vector_to_array(col("probability"))) \
                         .withColumn("fraud_score", col("prob_array")[1])

# 10. Đánh giá Precision@200 & PR-AUC
w_score = Window.orderBy(col("fraud_score").desc())
top_200 = predictions.withColumn("rank", row_number().over(w_score)).filter(col("rank") <= 200)

tp_count = top_200.filter(col(target_col) == 1.0).count()
precision_at_200 = tp_count / min(200.0, test_df.count())

evaluator_pr = BinaryClassificationEvaluator(
    labelCol=target_col, 
    rawPredictionCol="probability", 
    metricName="areaUnderPR"
)
pr_auc = evaluator_pr.evaluate(predictions)

print("\n=== KẾT QUẢ ĐÁNH GIÁ MÔ HÌNH ===")
print(f"-> Precision@200: {precision_at_200:.4f}")
print(f"-> PR-AUC:        {pr_auc:.4f}")

# 11. Lưu Model bằng đường dẫn tuyệt đối
BASE_DIR = r"D:\Homework\BigData_CT5_7-9"
model_dir = os.path.join(BASE_DIR, "models").replace("\\", "/")
os.makedirs(model_dir, exist_ok=True)

model_path = os.path.join(model_dir, "gbt_fraud_model").replace("\\", "/")

model.write().overwrite().save(model_path)
print(f"--> Đã lưu mô hình thành công tại: {model_path}")