import os
import sys

# 1. Cau hinh moi truong Python, Java & Hadoop
os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

os.environ["JAVA_HOME"] = r"D:\Homework\Java\OpenJDK17U-jdk_x64_windows_hotspot_17.0.20.1_1\jdk-17.0.20.1+1"
os.environ["HADOOP_HOME"] = r"D:\Homework\Hadoop"
os.environ["PATH"] = (
    os.path.join(os.environ["JAVA_HOME"], "bin") + os.pathsep +
    os.path.join(os.environ["HADOOP_HOME"], "bin") + os.pathsep +
    os.path.join(os.environ["HADOOP_HOME"], "sbin") + os.pathsep +
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

# 2. Khoi tao Spark Session tich hop Delta Lake
builder = SparkSession.builder \
    .appName("TrainFraudDetectionModel") \
    .master("local[*]") \
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
    .config("spark.driver.memory", "2g")

spark = configure_spark_with_delta_pip(builder).getOrCreate()
spark.sparkContext.setLogLevel("WARN")

# 3. Doc du lieu tu Delta Lake Silver (Sua lai duong dan dung chung dang relative/absolute an toan)
print("--> Dang tai du lieu huan luyen tu Delta Lake Silver...")
SILVER_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../delta_lake/silver/giao_dich"))

if not os.path.exists(SILVER_PATH):
    # Fallback neu duong dan khac cau truc
    SILVER_PATH = r"D:\Homework\BigData_CT5_7-9\delta_lake\silver\giao_dich"

df = spark.read.format("delta").load(SILVER_PATH)

# 4. Xac dinh cot nhan & Ep kieu du lieu ve DoubleType
target_col = "isFraud_Goc" 
df = df.withColumn(target_col, col(target_col).cast(DoubleType()))

# 5. Phan chia Stratified Split
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

print(f"Tong so ban ghi: {total_rows}")
print(f"-> Train: {train_df.count()} | So gian lan (1): {train_pos}")
print(f"-> Val:   {val_df.count()} | So gian lan (1): {val_pos}")
print(f"-> Test:  {test_df.count()} | So gian lan (1): {test_pos}")

# 6. Xu ly mat can bang du lieu tren tap Train
num_pos = train_pos
num_neg = train_df.count() - num_pos
pos_weight = float(num_neg) / float(num_pos) if num_pos > 0 else 1.0

train_df = train_df.withColumn("weight", when(col(target_col) == 1.0, pos_weight).otherwise(1.0))

# 7. Loc danh sach dac trung dang so
exclude_cols = ["Class", "is_fraud", "isFraud_Goc", "row_id", "weight", "Time", "event_datetime", "ma_giao_dich", "thoi_diem", "thoi_diem_nhan", "tai_khoan_nguon", "tai_khoan_dich", "loai", "kenh", "ngay"]
feature_cols = [
    field.name for field in df.schema.fields 
    if isinstance(field.dataType, NumericType) and field.name not in exclude_cols
]

print(f"--> So luong dac trung dang so dua vao mo hinh: {len(feature_cols)}")

assembler = VectorAssembler(inputCols=feature_cols, outputCol="raw_features", handleInvalid="skip")
scaler = StandardScaler(inputCol="raw_features", outputCol="features", withStd=True, withMean=True)

# 8. Cau hinh & Huan luyen GBTClassifier
gbt = GBTClassifier(
    labelCol=target_col, 
    featuresCol="features", 
    weightCol="weight",
    maxDepth=5, 
    maxIter=20, 
    seed=42
)

pipeline = Pipeline(stages=[assembler, scaler, gbt])

print("--> Dang huan luyen mo hinh GBTClassifier...")
model = pipeline.fit(train_df)

# 9. Du doan tren tap Test
predictions = model.transform(test_df)
predictions = predictions.withColumn("prob_array", vector_to_array(col("probability"))) \
                         .withColumn("fraud_score", col("prob_array")[1])

# 10. Danh gia Precision@200 & PR-AUC
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

print("\n=== KET QUA DANH GIA MO HINH ===")
print(f"-> Precision@200: {precision_at_200:.4f}")
print(f"-> PR-AUC:        {pr_auc:.4f}")

# 11. Luu Model bang duong dan tuyet doi
BASE_DIR = r"D:\Homework\BigData_CT5_7-9"
model_dir = os.path.join(BASE_DIR, "models").replace("\\", "/")
os.makedirs(model_dir, exist_ok=True)

model_path = os.path.join(model_dir, "gbt_fraud_model").replace("\\", "/")

model.write().overwrite().save(model_path)
print(f"--> Da luu mo hinh thanh cong tai: {model_path}")