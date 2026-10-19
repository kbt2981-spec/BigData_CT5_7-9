import os
import sys
import numpy as np
import pandas as pd
from datetime import datetime

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
from pyspark.sql.functions import col, lit, current_date
from delta import configure_spark_with_delta_pip

def calculate_psi(expected, actual, num_buckets=10):
    """
    Tinh Population Stability Index (PSI) giua phan phoi goc (expected) va hien tai (actual)
    PSI < 0.1: On dinh (khong drift)
    0.1 <= PSI <= 0.25: Canh bao (co su thay doi nhe)
    PSI > 0.25: Nghiêm trọng (can retrain mo hinh)
    """
    expected = np.array(expected, dtype=float)
    actual = np.array(actual, dtype=float)

    expected = expected[~np.isnan(expected)]
    actual = actual[~np.isnan(actual)]

    if len(expected) == 0 or len(actual) == 0:
        return 0.0

    # Chia bins theo phan vi cua tap baseline
    percentiles = np.linspace(0, 100, num_buckets + 1)
    bins = np.percentile(expected, percentiles)
    bins[0] = -np.inf
    bins[-1] = np.inf
    bins = np.unique(bins)

    if len(bins) < 2:
        return 0.0

    exp_counts, _ = np.histogram(expected, bins=bins)
    act_counts, _ = np.histogram(actual, bins=bins)

    # Chuan hoa ve ty le phan tram + them epsilon chong chia cho 0
    eps = 1e-4
    exp_pct = (exp_counts / len(expected)) + eps
    act_pct = (act_counts / len(actual)) + eps

    exp_pct = exp_pct / np.sum(exp_pct)
    act_pct = act_pct / np.sum(act_pct)

    psi_val = np.sum((act_pct - exp_pct) * np.log(act_pct / exp_pct))
    return float(psi_val)

def calculate_ks(expected, actual):
    """
    Tinh Kolmogorov-Smirnov statistic giua 2 phan phoi
    """
    try:
        from scipy.stats import ks_2samp
        res = ks_2samp(expected, actual)
        return float(res.statistic)
    except Exception:
        # Fallback tinh thu cong neu thieu scipy
        expected = np.sort(expected)
        actual = np.sort(actual)
        all_vals = np.concatenate([expected, actual])
        cdf_exp = np.searchsorted(expected, all_vals, side='right') / len(expected)
        cdf_act = np.searchsorted(actual, all_vals, side='right') / len(actual)
        return float(np.max(np.abs(cdf_exp - cdf_act)))

def run_drift_analysis():
    print("=== [AIRFLOW TASK] TIEN HANH PHAN TICH DATA DRIFT (PSI & KS) ===")
    
    builder = SparkSession.builder \
        .appName("DataDriftAnalysis") \
        .master("local[*]") \
        .config("spark.driver.memory", "2g") \
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")

    spark = configure_spark_with_delta_pip(builder).getOrCreate()
    spark.sparkContext.setLogLevel("WARN")

    PROJECT_DIR = r"D:\Homework\BigData_CT5_7-9"
    SILVER_PATH = os.path.join(PROJECT_DIR, "delta_lake", "silver", "giao_dich").replace("\\", "/")
    DRIFT_GOLD_PATH = os.path.join(PROJECT_DIR, "delta_lake", "gold", "theo_doi_drift").replace("\\", "/")

    if not os.path.exists(SILVER_PATH):
        print(f"[!] Khong tim thay du lieu Silver tai: {SILVER_PATH}. Su dung gia tri mac dinh.")
        return 0.05

    df = spark.read.format("delta").load(SILVER_PATH)
    total_count = df.count()
    if total_count < 20:
        print("[!] Du lieu qua it de tinh toan drift. Gia tri PSI mac dinh = 0.02 (on_dinh).")
        return 0.02

    # Lay phan vi 70% de gia lap tap huan luyen cu vs 30% con lai (cua so moi)
    split_done = False
    if "step" in df.columns:
        step_non_null = df.filter(col("step").isNotNull()).count()
        if step_non_null > 0:
            q = df.approxQuantile("step", [0.70], 0.01)
            if q and len(q) > 0 and q[0] is not None:
                step_70 = q[0]
                base_df = df.filter(col("step") <= step_70)
                curr_df = df.filter(col("step") > step_70)
                if base_df.count() > 0 and curr_df.count() > 0:
                    split_done = True
    if not split_done:
        base_df, curr_df = df.randomSplit([0.7, 0.3], seed=42)

    features_to_check = ["so_tien", "oldbalanceOrg", "newbalanceOrig"]
    drift_records = []
    max_psi = 0.0

    today_str = datetime.now().strftime("%Y-%m-%d")

    for feat in features_to_check:
        if feat in df.columns:
            base_vals = [r[0] for r in base_df.select(feat).na.drop().sample(fraction=min(1.0, 10000.0/total_count), seed=42).collect()]
            curr_vals = [r[0] for r in curr_df.select(feat).na.drop().sample(fraction=min(1.0, 10000.0/total_count), seed=42).collect()]
            
            psi = calculate_psi(base_vals, curr_vals)
            ks = calculate_ks(base_vals, curr_vals)

            if psi > max_psi:
                max_psi = psi

            if psi < 0.1:
                muc_do = "on_dinh"
            elif psi <= 0.25:
                muc_do = "canh_bao"
            else:
                muc_do = "nghiem_trong"

            print(f"--> Dac trung: {feat:<18} | PSI: {psi:.4f} | KS: {ks:.4f} | Muc do: {muc_do}")
            drift_records.append((today_str, feat, float(psi), float(ks), muc_do))

    # Ghi ket qua vao bang Delta gold.theo_doi_drift
    if drift_records:
        try:
            from deltalake import write_deltalake
            pdf = pd.DataFrame(drift_records, columns=["ngay", "ten_dac_trung", "psi", "ks_statistic", "muc_do"])
            write_deltalake(DRIFT_GOLD_PATH, pdf, mode="append")
            print(f"--> Da ghi ket qua vao Delta Table (qua deltalake-rs): {DRIFT_GOLD_PATH}")
        except Exception as e_delta:
            drift_spark_df = spark.createDataFrame(
                drift_records, 
                ["ngay", "ten_dac_trung", "psi", "ks_statistic", "muc_do"]
            )
            drift_spark_df.write \
                .format("delta") \
                .mode("append") \
                .option("mergeSchema", "true") \
                .save(DRIFT_GOLD_PATH)
            print(f"--> Da ghi ket qua vao Delta Table (qua Spark): {DRIFT_GOLD_PATH}")

    return max_psi

if __name__ == "__main__":
    max_psi = run_drift_analysis()
    print(f"\n[FINAL_MAX_PSI]: {max_psi:.4f}")
