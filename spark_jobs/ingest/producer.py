import os
import pandas as pd
import json
import time
import random
import uuid
from datetime import datetime, timedelta
from kafka import KafkaProducer

# Khởi tạo Kafka Producer
producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

TOPIC_NAME = 'transactions'

# Đường dẫn đến các thư mục dữ liệu
PAYSIM_DIR = r"D:\Homework\BigData_CT5_7-9\PaySim"
CREDITCARD_DIR = r"D:\Homework\BigData_CT5_7-9\archive"

# Chọn nguồn dữ liệu bạn muốn chạy (Ví dụ: chọn 'paysim' hoặc 'creditcard')
CHON_NGUON_DU_LIEU = "paysim" 

if CHON_NGUON_DU_LIEU == "paysim":
    FILE_NAME = "PS_20174392719_1491204439457_log.csv" # Đảm bảo tên file khớp thực tế trong thư mục PaySim
    file_path = os.path.join(PAYSIM_DIR, FILE_NAME)
    print(f"Đang đọc dữ liệu PaySim từ: {file_path}...")
    df = pd.read_csv(file_path)
    
    # Giả lập streaming theo step của PaySim
    steps = sorted(df['step'].unique())
    for current_step in steps:
        step_data = df[df['step'] == current_step]
        print(f"Đang phát Step {current_step} - {len(step_data)} giao dịch...")
        
        for _, row in step_data.iterrows():
            thoi_diem_nhan = datetime.now()
            delay_seconds = random.randint(1, 30) if random.random() < 0.2 else 0
            thoi_diem = thoi_diem_nhan - timedelta(seconds=delay_seconds)
            
            giao_dich = {
                "ma_giao_dich": str(uuid.uuid4()),
                "thoi_diem": thoi_diem.strftime("%Y-%m-%d %H:%M:%S"),
                "thoi_diem_nhan": thoi_diem_nhan.strftime("%Y-%m-%d %H:%M:%S"),
                "tai_khoan_nguon": row['nameOrig'],
                "tai_khoan_dich": row['nameDest'],
                "loai": row['type'],
                "so_tien": float(row['amount']),
                "so_du_truoc_nguon": float(row['oldbalanceOrg']),
                "so_du_sau_nguon": float(row['newbalanceOrig']),
                "so_du_truoc_dich": float(row['oldbalanceDest']),
                "so_du_sau_dich": float(row['newbalanceDest']),
                "kenh": "APP",
                "isFraud_Goc": int(row['isFraud'])
            }
            producer.send(TOPIC_NAME, giao_dich)
        
        producer.flush()
        time.sleep(10) # 1 step mô phỏng tương ứng 10 giây thực tế

elif CHON_NGUON_DU_LIEU == "creditcard":
    FILE_NAME = "creditcard.csv" # Tên file phổ biến trong bộ dữ liệu ULB Credit Card Fraud
    file_path = os.path.join(CREDITCARD_DIR, FILE_NAME)
    print(f"Đang đọc dữ liệu Credit Card từ: {file_path}...")
    df = pd.read_csv(file_path)
    
    # Vì Credit Card không có cột 'step', ta chia nhỏ dữ liệu thành các lô (batch) giả lập streaming
    batch_size = 1000
    for i in range(0, len(df), batch_size):
        batch_data = df.iloc[i:i+batch_size]
        print(f"Đang phát lô giao dịch từ dòng {i} đến {i+len(batch_data)}...")
        
        for _, row in batch_data.iterrows():
            thoi_diem_nhan = datetime.now()
            delay_seconds = random.randint(1, 30) if random.random() < 0.2 else 0
            thoi_diem = thoi_diem_nhan - timedelta(seconds=delay_seconds)
            
            giao_dich = {
                "ma_giao_dich": str(uuid.uuid4()),
                "thoi_diem": thoi_diem.strftime("%Y-%m-%d %H:%M:%S"),
                "thoi_diem_nhan": thoi_diem_nhan.strftime("%Y-%m-%d %H:%M:%S"),
                "tai_khoan_nguon": f"CC_User_{row.get('V1', 'unknown')}", # Đóng gói giả lập cho thẻ tín dụng
                "tai_khoan_dich": "MERCHANT_UNKNOWN",
                "loai": "CC_PAYMENT",
                "so_tien": float(row['Amount']),
                "so_du_truoc_nguon": 0.0,
                "so_du_sau_nguon": 0.0,
                "so_du_truoc_dich": 0.0,
                "so_du_sau_dich": 0.0,
                "kenh": "POS",
                "isFraud_Goc": int(row['Class'])
            }
            producer.send(TOPIC_NAME, giao_dich)
            
        producer.flush()
        time.sleep(5)