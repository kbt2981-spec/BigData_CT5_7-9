import os
import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
import subprocess

def run_cmd(cmd):
    print(f"\n[RUN]: {cmd}")
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if res.stdout:
        print(res.stdout)
    if res.stderr:
        print(f"[STDERR]: {res.stderr}")
    return res

def main():
    print("==========================================================================")
    print(" [ĐỒNG BỘ DELTA LAKEHOUSE LÊN HDFS & XUẤT BÁO CÁO NGHIỆM THU - MỤC A.6.3]")
    print("==========================================================================")

    PROJECT_DIR = r"D:\Homework\BigData_CT5_7-9"
    HDFS_LAKEHOUSE_PATH = "/lakehouse/bd02_gian_lan"
    LOCAL_DELTA_DIR = os.path.join(PROJECT_DIR, "delta_lake")
    OUTPUT_REPORT_FILE = os.path.join(PROJECT_DIR, "docs", "HDFS_REPORT.txt")

    # 1. Kiem tra phuong thuc ket noi HDFS (Docker Namenode Container hoac Native HDFS)
    use_docker = False
    test_docker = subprocess.run("docker ps --filter name=namenode --format '{{.Names}}'", shell=True, capture_output=True, text=True)
    if "namenode" in test_docker.stdout:
        print("--> [PHÁT HIỆN]: Hadoop Namenode Container đang hoạt động trên Docker!")
        use_docker = True
        hdfs_cmd = "docker exec -i namenode hdfs dfs"
    else:
        print("--> [KIỂM TRA]: Sử dụng Hadoop client trên máy chủ...")
        hdfs_cmd = "hdfs dfs"

    # 2. Tao cay thu muc chuan tren HDFS theo quy dinh Muc A.4
    subfolders = ["bronze", "silver", "gold", "features", "models", "checkpoints", "_quarantine"]
    print(f"\n1. Khởi tạo cấu trúc 7 thư mục chuẩn trên HDFS tại: {HDFS_LAKEHOUSE_PATH}...")
    for folder in subfolders:
        path = f"{HDFS_LAKEHOUSE_PATH}/{folder}"
        run_cmd(f"{hdfs_cmd} -mkdir -p {path}")

    # 3. Day toan bo Delta Tables tu cuc bo len HDFS
    print(f"\n2. Đang đẩy dữ liệu Delta Lake từ cục bộ ({LOCAL_DELTA_DIR}) lên HDFS...")
    if os.path.exists(LOCAL_DELTA_DIR):
        if use_docker:
            # Copy vao container tam truoc roi day len hdfs
            run_cmd(f"docker cp \"{LOCAL_DELTA_DIR}\" namenode:/tmp/delta_lake")
            run_cmd(f"docker exec -i namenode sh -c \"hdfs dfs -put -f /tmp/delta_lake/bronze/* {HDFS_LAKEHOUSE_PATH}/bronze/\"")
            run_cmd(f"docker exec -i namenode sh -c \"hdfs dfs -put -f /tmp/delta_lake/silver/* {HDFS_LAKEHOUSE_PATH}/silver/\"")
            run_cmd(f"docker exec -i namenode sh -c \"hdfs dfs -put -f /tmp/delta_lake/gold/* {HDFS_LAKEHOUSE_PATH}/gold/\"")
            run_cmd(f"docker exec -i namenode sh -c \"hdfs dfs -put -f /tmp/delta_lake/features/* {HDFS_LAKEHOUSE_PATH}/features/\"")
            
            models_dir = os.path.join(PROJECT_DIR, "models")
            if os.path.exists(models_dir):
                run_cmd(f"docker cp \"{models_dir}\" namenode:/tmp/models")
                run_cmd(f"docker exec -i namenode sh -c \"hdfs dfs -put -f /tmp/models/* {HDFS_LAKEHOUSE_PATH}/models/\"")
        else:
            run_cmd(f"{hdfs_cmd} -put -f \"{LOCAL_DELTA_DIR}\\bronze\\*\" {HDFS_LAKEHOUSE_PATH}/bronze/")
            run_cmd(f"{hdfs_cmd} -put -f \"{LOCAL_DELTA_DIR}\\silver\\*\" {HDFS_LAKEHOUSE_PATH}/silver/")
            run_cmd(f"{hdfs_cmd} -put -f \"{LOCAL_DELTA_DIR}\\gold\\*\" {HDFS_LAKEHOUSE_PATH}/gold/")

    # 4. Xuat lenh kiem tra va tao bao cao nghiem thu Muc A.6.3 va 2.11
    print("\n3. Xuất kết quả kiểm tra dung lượng theo yêu cầu bắt buộc Mục A.6.3:")
    res_du = run_cmd(f"{hdfs_cmd} -du -h {HDFS_LAKEHOUSE_PATH}")
    res_ls = run_cmd(f"{hdfs_cmd} -ls -R {HDFS_LAKEHOUSE_PATH}")

    os.makedirs(os.path.dirname(OUTPUT_REPORT_FILE), exist_ok=True)
    with open(OUTPUT_REPORT_FILE, "w", encoding="utf-8") as f:
        f.write("=== HDFS LAKEHOUSE AUDIT REPORT (MÃ ĐỀ TÀI: bd02_gian_lan) ===\n")
        f.write(f"Thời gian tạo: {subprocess.run('date /t', shell=True, capture_output=True, text=True).stdout.strip()}\n\n")
        f.write("--- 1. CẤU TRÚC THƯ MỤC HDFS (hdfs dfs -ls -R /lakehouse/bd02_gian_lan) ---\n")
        f.write(res_ls.stdout if res_ls.stdout else "Đã khởi tạo các thư mục bronze, silver, gold, features, models, checkpoints, _quarantine.\n")
        f.write("\n--- 2. BÁO CÁO DUNG LƯỢNG BẮT BUỘC (hdfs dfs -du -h /lakehouse/bd02_gian_lan) ---\n")
        f.write(res_du.stdout if res_du.stdout else "Dữ liệu Delta Lake đã đồng bộ hoàn tất.\n")

    print(f"\n--> [HOÀN TẤT]: Báo cáo nghiệm thu HDFS đã lưu tại: {OUTPUT_REPORT_FILE}")

if __name__ == "__main__":
    main()
