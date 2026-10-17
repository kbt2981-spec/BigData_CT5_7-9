# NHẬT KÝ THỰC HIỆN ĐỒ ÁN BIG DATA

## 1. Thông tin thành viên & Đóng góp
* **Họ và tên:** Lê Thanh Phong 
* **MSSV:** 2001230669
* **Đề tài:** Hệ thống phát hiện gian lận giao dịch tài chính (Financial Fraud Detection - PaySim)
* **Phân công công việc:** 
  * Xây dựng hạ tầng, cấu hình Docker và quản lý dữ liệu lớn bằng Apache Spark & Delta Lake.
  * Thiết kế luồng tự động hóa quy trình (Pipeline) với Apache Airflow.
  * Huấn luyện mô hình học máy GBT Classifier và phát triển ứng dụng web Backend (FastAPI) kết hợp Frontend (HTML/Bootstrap).
  * Quản lý mã nguồn, tối ưu hóa dung lượng repository và xử lý các sự cố Git.

---

## 2. Mốc thời gian và Tiến độ công việc

### Tuần 1: Khảo sát bài toán, Xây dựng hạ tầng & Huấn luyện mô hình
* **Ngày 1 - 2:** Nghiên cứu bài toán phát hiện gian lận tài chính trên tập dữ liệu PaySim (hơn 6.3 triệu bản ghi). Thiết lập môi trường phát triển chung bằng Docker và Docker Compose.
* **Ngày 3 - 4:** Sử dụng Apache Spark để nạp dữ liệu thô, xây dựng các tầng lưu trữ phân tán (Bronze/Silver tables) sử dụng định dạng Delta Lake / Parquet nhằm tối ưu hóa hiệu suất truy vấn và đảm bảo tính nhất quán.
* **Ngày 5 - 7:** Tiền xử lý dữ liệu, trích xuất đặc trưng, sử dụng `StandardScaler` và tiến hành huấn luyện mô hình học máy **GBT Classifier** (Gradient-Boosted Trees) để giải quyết bài toán mất cân bằng dữ liệu gian lận. Xây dựng các tệp Airflow DAGs (`dags/`) để chuẩn bị tự động hóa pipeline.

### Tuần 2: Phát triển ứng dụng, Tích hợp hệ thống & Kiểm thử
* **Ngày 8 - 10:** Phát triển tầng Backend API bằng **FastAPI** (`webapp/backend/main.py`) để tích hợp mô hình đã huấn luyện, cho phép thực hiện dự đoán thời gian thực (real-time inference). Xây dựng giao diện Web Dashboard bằng HTML/Bootstrap.
* **Ngày 11 - 14:** Đóng gói ứng dụng, viết các script tiện ích (`run_all.bat`, `stop_all.bat`), tiến hành kiểm thử toàn bộ hệ thống và thực hiện dọn dẹp mã nguồn để chuẩn bị nộp bài.

---

## 3. Các lỗi thực tế gặp phải và Biện pháp khắc phục

Trong quá trình triển khai dự án trên môi trường thực tế, nhóm đã gặp và giải quyết các vấn đề kỹ thuật sau:

1. **Lỗi phình to dung lượng kho lưu trữ Git (14GB+) và vượt giới hạn GitHub:**
   * **Nguyên nhân:** Thư mục môi trường ảo `.venv/`, thư mục dữ liệu `delta_lake/`, các file nén dữ liệu lớn (`PaySim.zip`, `archive.zip`) và thư mục hệ thống WSL của Docker bị Git theo dõi nhầm. File cài đặt `Docker Desktop Installer.exe` nặng gần 600MB vi phạm giới hạn 100MB của GitHub.
   * **Cách khắc phục:** 
     * Xây dựng chuẩn file `.gitignore` đặt tại thư mục gốc để chặn toàn bộ các thành phần nặng và tệp tạm.
     * Sử dụng lệnh `git rm -r --cached` để xóa sạch các file/thư mục nặng khỏi bộ nhớ đệm của Git mà không làm mất dữ liệu thực tế trên máy.
     * Thêm quy tắc chặn định dạng file `.exe` và loại bỏ hoàn toàn các tệp tin vượt dung lượng cho phép.

2. **Lỗi Git không nhận diện quy tắc trong `.gitignore`:**
   * **Nguyên nhân:** File `.gitignore` trước đó bị đặt nhầm vị trí vào bên trong thư mục con (`.venv`), khiến Git không đọc được cấu hình chặn.
   * **Cách khắc phục:** Di chuyển file `.gitignore` ra ngoài cùng thư mục gốc của dự án (`D:\Homework\BigData_CT5_7-9\.gitignore`), sau đó thực hiện lệnh làm sạch cache và commit lại từ đầu.

---

## 4. Lịch sử Commit tiêu biểu trên GitHub
* `Initial clean commit for project source code`: Khởi tạo kho mã nguồn sạch, chỉ chứa mã nguồn ứng dụng, cấu hình Airflow và mã huấn luyện mô hình.
* `Update gitignore rules`: Cấu hình bộ lọc bỏ qua các tệp tin tạm, thư mục ảo và dữ liệu lớn.
* `Remove heavy models and venv from tracking`: Loại bỏ các file nhị phân lớn và môi trường ảo khỏi hệ thống theo dõi phiên bản.