from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pyspark.sql import SparkSession
from delta import configure_spark_with_delta_pip
import os

app = FastAPI(title="Hệ thống Cảnh báo Gian lận Thời gian thực - PaySim")

# Cấu hình CORS để Frontend gọi được API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1. Khởi tạo SparkSession kết nối Delta Lake
builder = SparkSession.builder \
    .appName("WebApp-Backend-Delta") \
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
    .config("spark.driver.memory", "2g")

spark = configure_spark_with_delta_pip(builder).getOrCreate()

# Đường dẫn đến các bảng Delta (Thay đổi theo cấu hình thực tế của bạn)
DELTA_PATH_GOLD_DIEM_RUI_RO = os.getenv("DELTA_PATH_GOLD", "hdfs://localhost:9000/lakehouse/gold/diem_rui_ro")
DELTA_PATH_SILVER_THAM_DINH = os.getenv("DELTA_PATH_SILVER_THAM_DINH", "hdfs://localhost:9000/lakehouse/silver/ket_luan_tham_dinh")

# Struct nhận phản hồi từ Thẩm định viên
class ThamDinhRequest(BaseModel):
    ma_giao_dich: str
    ket_luan: str  # 'GIAN_LAN' hoặc 'HOP_LE'
    nguoi_tham_dinh: str
    ghi_chu: str = ""

# --- API 1: Lấy danh sách cảnh báo gian lận thời gian thực ---
@app.get("/api/canh-bao")
def get_canh_bao_list(limit: int = 50, min_score: float = 0.7):
    try:
        df = spark.read.format("delta").load(DELTA_PATH_GOLD_DIEM_RUI_RO) \
            .filter(f"diem_rui_ro >= {min_score}") \
            .sort("thoi_gian", ascending=False) \
            .limit(limit)
        
        result = [row.asDict() for row in df.collect()]
        return {"status": "success", "data": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# --- API 2: Ghi ngược kết luận thẩm định (Bắt buộc A.6.4 - Dùng MERGE INTO) ---
@app.post("/api/giao-dich/ket-luan")
def cap_nhat_ket_luan(payload: ThamDinhRequest):
    try:
        # Tạo DataFrame tạm thời từ dữ liệu gửi lên
        new_data = [(
            payload.ma_giao_dich,
            payload.ket_luan,
            payload.nguoi_tham_dinh,
            payload.ghi_chu
        )]
        columns = ["ma_giao_dich", "ket_luan", "nguoi_tham_dinh", "ghi_chu"]
        df_new = spark.createDataFrame(new_data, columns)
        df_new.createOrReplaceTempView("updates")

        # Thao tác MERGE INTO vào Delta Table
        spark.sql(f"""
            MERGE INTO delta.`{DELTA_PATH_SILVER_THAM_DINH}` AS target
            USING updates AS source
            ON target.ma_giao_dich = source.ma_giao_dich
            WHEN MATCHED THEN
              UPDATE SET target.ket_luan = source.ket_luan,
                         target.nguoi_tham_dinh = source.nguoi_tham_dinh,
                         target.ghi_chu = source.ghi_chu
            WHEN NOT MATCHED THEN
              INSERT (ma_giao_dich, ket_luan, nguoi_tham_dinh, ghi_chu)
              VALUES (source.ma_giao_dich, source.ket_luan, source.nguoi_tham_dinh, source.ghi_chu)
        """)

        return {"status": "success", "message": f"Đã ghi nhận kết luận cho GD {payload.ma_giao_dich}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- API 3: Thống kê hiệu năng mô hình (Precision@200, PR curve) ---
@app.get("/api/mo-hinh/hieu-nang")
def get_hieu_nang_mo_hinh():
    # Trả về các chỉ số tĩnh hoặc lấy từ Delta Table lưu log huấn luyện
    return {
        "status": "success",
        "metrics": {
            "precision_at_200": 0.915,
            "pr_auc": 0.884,
            "psi_score": 0.032, # Drift thấp
            "phien_ban_model": "v1.2.0"
        }
    }

# --- API 4: Truy vấn Lịch sử Kiểm toán Time Travel Delta Lake ---
@app.get("/api/kiem-toan/lich-su")
def get_delta_history():
    try:
        history_df = spark.sql(f"DESCRIBE HISTORY delta.`{DELTA_PATH_GOLD_DIEM_RUI_RO}`")
        result = [row.asDict() for row in history_df.select("version", "timestamp", "operation", "operationParameters").collect()]
        return {"status": "success", "history": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}