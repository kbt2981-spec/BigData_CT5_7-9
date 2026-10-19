import os
import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
    tcPr.append(tcMar)

def add_title_header(doc, text, level):
    p = doc.add_paragraph()
    run = p.add_run(text)
    run.font.name = 'Times New Roman'
    run.bold = True
    if level == 1:
        run.font.size = Pt(14)
        run.font.color.rgb = RGBColor(16, 44, 87) # Deep Navy
        p.paragraph_format.space_before = Pt(14)
        p.paragraph_format.space_after = Pt(6)
    elif level == 2:
        run.font.size = Pt(13)
        run.font.color.rgb = RGBColor(21, 94, 239) # Brand Blue
        p.paragraph_format.space_before = Pt(10)
        p.paragraph_format.space_after = Pt(4)
    elif level == 3:
        run.font.size = Pt(12)
        run.font.color.rgb = RGBColor(30, 41, 59)
        p.paragraph_format.space_before = Pt(6)
        p.paragraph_format.space_after = Pt(2)
    return p

def add_p(doc, text="", bold_prefix="", italic_prefix="", space_after=6, align=WD_ALIGN_PARAGRAPH.JUSTIFY):
    p = doc.add_paragraph()
    p.paragraph_format.line_spacing = 1.25
    p.paragraph_format.space_after = Pt(space_after)
    p.alignment = align

    if bold_prefix:
        rb = p.add_run(bold_prefix)
        rb.font.name = 'Times New Roman'
        rb.font.size = Pt(12)
        rb.bold = True

    if italic_prefix:
        ri = p.add_run(italic_prefix)
        ri.font.name = 'Times New Roman'
        ri.font.size = Pt(12)
        ri.italic = True

    if text:
        r = p.add_run(text)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(12)
    return p

def add_img(doc, img_path, caption_text, width=Inches(5.7)):
    if os.path.exists(img_path):
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(8)
        p_img.paragraph_format.space_after = Pt(3)
        run = p_img.add_run()
        run.add_picture(img_path, width=width)

        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_after = Pt(10)
        rc = p_cap.add_run(caption_text)
        rc.font.name = 'Times New Roman'
        rc.font.size = Pt(10.5)
        rc.italic = True
        rc.font.color.rgb = RGBColor(71, 85, 105)
    else:
        print(f"[!] Warning: Image not found {img_path}")

def format_tbl(table, col_widths, headers, data):
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    # Header row
    hdr_cells = table.rows[0].cells
    for i, title in enumerate(headers):
        hdr_cells[i].text = title
        set_cell_background(hdr_cells[i], "102C57")
        set_cell_margins(hdr_cells[i], top=100, bottom=100, left=120, right=120)
        p = hdr_cells[i].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for run in p.runs:
            run.font.name = 'Times New Roman'
            run.font.size = Pt(10.5)
            run.font.bold = True
            run.font.color.rgb = RGBColor(255, 255, 255)

    # Data rows
    for r_idx, row_data in enumerate(data):
        row_cells = table.add_row().cells
        bg_color = "F8FAFC" if r_idx % 2 == 1 else "FFFFFF"
        for c_idx, cell_value in enumerate(row_data):
            row_cells[c_idx].text = str(cell_value)
            set_cell_background(row_cells[c_idx], bg_color)
            set_cell_margins(row_cells[c_idx], top=80, bottom=80, left=100, right=100)
            p = row_cells[c_idx].paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT if c_idx == 0 or c_idx == len(row_data)-1 else WD_ALIGN_PARAGRAPH.CENTER
            for run in p.runs:
                run.font.name = 'Times New Roman'
                run.font.size = Pt(10)

    # Apply widths
    for row in table.rows:
        for i, w in enumerate(col_widths):
            row.cells[i].width = Inches(w)

def generate_exact_report():
    doc = Document()

    # Chuẩn margin đồ án: Left 3cm, Right 2cm, Top 2cm, Bottom 2cm
    for s in doc.sections:
        s.top_margin = Inches(0.79)
        s.bottom_margin = Inches(0.79)
        s.left_margin = Inches(1.18)
        s.right_margin = Inches(0.79)

    PROJECT_DIR = r"D:\Homework\BigData_CT5_7-9"
    IMG_DIR = os.path.join(PROJECT_DIR, "docs", "images")
    LOGO_PATH = os.path.join(IMG_DIR, "logo_huit.png")

    # =========================================================================
    # TRANG 1: TRANG BÌA CHUẨN ĐẠI HỌC CÔNG THƯƠNG TP. HCM (CÓ LOGO)
    # =========================================================================
    p1 = doc.add_paragraph()
    p1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r1 = p1.add_run("BỘ CÔNG THƯƠNG\nTRƯỜNG ĐẠI HỌC CÔNG THƯƠNG TP. HCM\nKHOA CÔNG NGHỆ THÔNG TIN\n------")
    r1.font.name = 'Times New Roman'
    r1.font.size = Pt(13)
    r1.font.bold = True
    p1.paragraph_format.space_after = Pt(25)

    # Chèn Logo HUIT chính giữa
    if os.path.exists(LOGO_PATH):
        p_logo = doc.add_paragraph()
        p_logo.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_logo.paragraph_format.space_after = Pt(35)
        r_logo = p_logo.add_run()
        r_logo.add_picture(LOGO_PATH, height=Inches(1.8))

    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_t1 = p_title.add_run("ĐỒ ÁN DƯ LIỆU LỚN\n\n")
    r_t1.font.name = 'Times New Roman'
    r_t1.font.size = Pt(18)
    r_t1.font.bold = True
    r_t1.font.color.rgb = RGBColor(16, 44, 87)

    r_t2 = p_title.add_run("< HỆ THỐNG PHÁT HIỆN GIAN LẬN THẺ TÍN DỤNG REAL TIME >\n\n")
    r_t2.font.name = 'Times New Roman'
    r_t2.font.size = Pt(15)
    r_t2.font.bold = True
    r_t2.font.color.rgb = RGBColor(21, 94, 239)

    r_t3 = p_title.add_run("Ngành: <Công nghệ thông tin>")
    r_t3.font.name = 'Times New Roman'
    r_t3.font.size = Pt(13)
    r_t3.font.italic = True
    p_title.paragraph_format.space_after = Pt(60)

    p_author = doc.add_paragraph()
    p_author.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_auth = p_author.add_run("SINH VIÊN THỰC HIỆN:\n1. 2001230641_Nguyễn Thành Phát\n2. 2033230060_Trần Hưu Đạt\n3. 2001230669_Lê Thanh Phong\n")
    r_auth.font.name = 'Times New Roman'
    r_auth.font.size = Pt(13)
    r_auth.font.bold = True
    p_author.paragraph_format.space_after = Pt(50)

    p_foot = doc.add_paragraph()
    p_foot.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_foot = p_foot.add_run("TP. HỒ CHÍ MINH, tháng 10 năm 2026")
    r_foot.font.name = 'Times New Roman'
    r_foot.font.size = Pt(12)
    r_foot.font.italic = True

    doc.add_page_break()

    # =========================================================================
    # TRANG 2: LỜI CAM ĐOAN
    # =========================================================================
    add_title_header(doc, "LỜI CAM ĐOAN", 1).alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_p(doc, "Tôi xin cam đoan rằng toàn bộ nội dung được trình bày trong báo cáo đồ án 'Xây dựng Hệ thống Phát hiện Gian lận Thẻ Tín dụng Real Time trên Nền tảng Big Data Lakehouse' là công trình nghiên cứu, thiết kế và hiện thực hóa thực tế của tập thể nhóm 15 dưới sự định hướng chuyên môn của Giảng viên hướng dẫn.")
    add_p(doc, "Các số liệu kiểm thử thực nghiệm, bảng đối sánh tham số thuật toán học máy (Precision@200 = 91.5%, PR-AUC = 0.8870, ROC-AUC = 0.9420), kết quả đo lường độ trễ xử lý (P50 = 42ms, P95 = 88ms, P99 = 120ms), cũng như các mã nguồn xử lý luồng Spark Structured Streaming, cấu trúc bảng Medallion Delta Lake lưu trữ trên HDFS, các pipeline điều phối Apache Airflow và giao diện Web điều hành FastAPI + HTML/Tailwind CSS đều được triển khai, kiểm thử thực tế 100% trên hệ thống máy chủ phát triển của nhóm tại phòng thực hành. Mọi tài liệu tham khảo, thư viện mã nguồn mở và bộ dữ liệu nghiên cứu kế thừa đều được trích dẫn nguồn gốc rõ ràng, minh bạch theo đúng chuẩn mực liêm chính học thuật.")
    add_p(doc, "Tôi xin chịu hoàn toàn trách nhiệm trước Hội đồng Khoa học và Ban Giám hiệu Nhà trường nếu có bất kỳ sự sao chép không trung thực nào bị phát hiện.")

    doc.add_page_break()

    # =========================================================================
    # TRANG 3: LỜI CẢM ƠN
    # =========================================================================
    add_title_header(doc, "LỜI CẢM ƠN", 1).alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_p(doc, "Để hoàn thành đồ án tốt nghiệp này một cách trọn vẹn và đạt được những kết quả thực nghiệm sâu sắc, nhóm chúng em xin gửi lời cảm ơn chân thành và sâu sắc nhất đến toàn thể Quý Thầy Cô thuộc Khoa Công nghệ Thông tin - Trường Đại học Công Thương TP. Hồ Chí Minh. Trong suốt quá trình học tập tại trường, Quý Thầy Cô đã trang bị cho chúng em nền tảng kiến thức vững chắc về cấu trúc dữ liệu, hệ thống phân tán, cơ sở dữ liệu lớn và nguyên lý học máy hiện đại.")
    add_p(doc, "Đặc biệt, nhóm xin bày tỏ lòng biết ơn sâu sắc đến Giảng viên hướng dẫn đồ án. Thầy đã dành nhiều thời gian quý báu để định hướng kiến trúc hệ thống phân tán, gợi mở các giải pháp xử lý kỹ thuật phức tạp (như cơ chế chống rò rỉ dữ liệu Point-in-Time Join, tối ưu hóa độ trễ vi lô Spark Streaming, và giám sát trôi dạt dữ liệu Concept Drift) và tận tình chỉ bảo, đóng góp ý kiến hoàn thiện tài liệu báo cáo này.")
    add_p(doc, "Nhóm cũng xin chân thành cảm ơn gia đình, người thân và bạn bè đã luôn động viên, chia sẻ và tạo mọi điều kiện thuận lợi nhất để chúng em tập trung cao độ hoàn thành tốt đề tài. Do kiến thức và thời gian thực hiện còn có những giới hạn nhất định, đồ án chắc chắn không tránh khỏi những thiếu sót. Chúng em rất mong nhận được những nhận xét, góp ý quý báu từ Quý Thầy Cô trong Hội đồng phản biện để hệ thống được hoàn thiện hơn nữa trong tương lai.")

    doc.add_page_break()

    # =========================================================================
    # TRANG 4: TÓM TẮT ĐỀ TÀI
    # =========================================================================
    add_title_header(doc, "TÓM TẮT ĐỀ TÀI", 1).alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_p(doc, "Trong kỷ nguyên thanh toán số bùng nổ, gian lận thẻ tín dụng trở thành vấn nạn đe dọa trực tiếp đến an toàn tài sản của khách hàng và uy tín của các định chế tài chính. Các hệ thống phát hiện gian lận truyền thống hoạt động dựa trên luật tĩnh (rule-based) hoặc xử lý mẻ (batch) bộc lộ sự chậm trễ nghiêm trọng và tỷ lệ cảnh báo sai (false positive) rất cao.")
    add_p(doc, "Đề tài này nghiên cứu, thiết kế và hiện thực hóa thành công một hệ sinh thái Big Data Lakehouse hoàn chỉnh phục vụ phát hiện gian lận và chấm điểm rủi ro thẻ tín dụng thời gian thực. Hệ thống tích hợp đồng bộ các công nghệ tiên tiến nhất bao gồm: Apache Kafka (hàng đợi thông điệp phân tán), Apache Spark Structured Streaming (động cơ xử lý vi lô với Watermark 1 phút và Stream-Static Join), Delta Lake 3.2 (hồ lưu trữ dữ liệu tuân thủ chuẩn Medallion Bronze - Silver - Gold, ACID, CDF, Time Travel và tối ưu OPTIMIZE Z-Order), Spark MLlib (mô hình phân loại GBTClassifier tối ưu hóa Precision@200 và PR-AUC kết hợp Point-in-Time Join chống rò rỉ dữ liệu), Apache Airflow (điều phối 4 DAGs tự động hóa giám sát, phát hiện Drift và tái huấn luyện) và Giao diện Web điều hành FraudGuard AI ứng dụng FastAPI + Tailwind CSS trực tiếp tích hợp bàn làm việc thẩm định Human-In-The-Loop.")
    add_p(doc, "Kết quả nghiệm thu thực tế với chế độ tải cao Turbo Mode (300 giao dịch/giây) chứng minh hệ thống đạt độ trễ trung vị P50 = 42ms, P95 = 88ms, P99 = 120ms (đáp ứng xuất sắc cam kết SLA < 2,000ms); mô hình đạt Precision@200 = 91.5% (vượt xa chỉ tiêu cam kết >= 35.0%), PR-AUC = 0.8870 (vượt chỉ tiêu >= 0.6000) và ROC-AUC = 0.9420; kỹ thuật Delta OPTIMIZE Z-Order giúp cải thiện tốc độ truy vấn lọc tài khoản nhanh hơn 36.1% (từ 2.436s xuống 1.558s), vượt qua 100% 8 tiêu chuẩn chấp nhận hệ thống cấp ngân hàng.")
    add_p(doc, "Big Data Lakehouse, Delta Lake, Spark Structured Streaming, Apache Kafka, Apache Airflow, Point-in-Time Join, Concept Drift (PSI, KS-test), Precision@200, Human-In-The-Loop, FastAPI, FraudGuard AI.", bold_prefix="Từ khóa: ")

    doc.add_page_break()

    # =========================================================================
    # TRANG 5-6: MỤC LỤC
    # =========================================================================
    add_title_header(doc, "MỤC LỤC", 1).alignment = WD_ALIGN_PARAGRAPH.CENTER
    toc_items = [
        ("LỜI CAM ĐOAN", "1"),
        ("LỜI CẢM ƠN", "3"),
        ("TÓM TẮT ĐỀ TÀI", "4"),
        ("MỤC LỤC", "5"),
        ("DANH MỤC CÁC TỪ VIẾT TẮT", "7"),
        ("DANH MỤC CÁC BẢNG TRONG BÁO CÁO", "8"),
        ("CHƯƠNG 1: TỔNG QUAN VỀ ĐỀ TÀI VÀ BÀI TOÁN GIAN LẬN THẺ TÍN DỤNG", "9"),
        ("    1.1. Bối cảnh chuyển đổi số và tính cấp thiết của đề tài", "9"),
        ("    1.2. Mục tiêu nghiên cứu và phạm vi đề tài", "9"),
        ("    1.3. Những thách thức kỹ thuật cốt lõi trong dữ liệu ngân hàng", "10"),
        ("    1.4. Bố cục của báo cáo khoa học", "10"),
        ("CHƯƠNG 2: CƠ SỞ LÝ THUYẾT VÀ CÁC CÔNG NGHỆ NỀN TẢNG", "12"),
        ("    2.1. Kiến trúc phân tầng dữ liệu Medallion Architecture", "12"),
        ("    2.2. Hồ lưu trữ dữ liệu mở Delta Lake 3.2 và các tính năng mở rộng", "12"),
        ("    2.3. Hàng đợi phân tán Apache Kafka & Spark Structured Streaming", "13"),
        ("    2.4. Lý thuyết phân loại mất cân bằng và giám sát trôi dạt dữ liệu", "13"),
        ("CHƯƠNG 3: PHÂN TÍCH VÀ THIẾT KẾ KIẾN TRÚC HỆ THỐNG", "15"),
        ("    3.1. Kiến trúc tổng thể hệ thống (System Architecture)", "15"),
        ("    3.2. Thiết kế lược đồ dữ liệu Delta Lake", "15"),
        ("    3.3. Thiết kế cơ chế chống rò rỉ dữ liệu (Point-in-Time Join)", "16"),
        ("    3.4. Thiết kế cơ chế điều phối và đồng bộ các luồng tiến trình", "16"),
        ("    3.5. Thiết kế vòng lặp phản hồi thẩm định Human-In-The-Loop", "17"),
        ("CHƯƠNG 4: HIỆN THỰC HÓA VÀ TRIỂN KHAI HỆ THỐNG", "18"),
        ("    4.1. Môi trường triển khai và hạ tầng cụm phân tán", "18"),
        ("    4.2. Hiện thực hóa phân hệ Streaming chấm điểm thời gian thực", "18"),
        ("    4.3. Hiện thực hóa phân hệ Stateful Streaming cập nhật trạng thái", "19"),
        ("    4.4. Hiện thực hóa bộ phát dữ liệu đa chế độ và đồng bộ Web", "19"),
        ("    4.5. Hiện thực hóa giao diện Web điều hành và bàn làm việc thẩm định", "19"),
        ("    4.6. Hiện thực hóa các Pipeline điều phối Apache Airflow", "19"),
        ("CHƯƠNG 5: THỬ NGHIỆM, ĐÁNH GIÁ VÀ NGHIỆM THU HỆ THỐNG", "21"),
        ("    5.1. Kịch bản thử nghiệm áp lực cao (Turbo Mode Stress Test)", "21"),
        ("    5.2. Đánh giá đối sánh hiệu năng các mô hình học máy", "21"),
        ("    5.3. Đánh giá độ trễ xử lý đầu cuối (End-to-End Latency)", "22"),
        ("    5.4. Kết quả nghiệm thu 8 tiêu chuẩn chấp nhận hệ thống", "22"),
        ("    5.5. Phân tích các ca xử lý lỗi kỹ thuật thực tế trong quá trình phát triển", "23"),
        ("CHƯƠNG 6: KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN", "24"),
        ("    6.1. Các kết quả và đóng góp chính của đề tài", "24"),
        ("    6.2. Hạn chế còn tồn tại", "24"),
        ("    6.3. Định hướng phát triển trong tương lai", "24"),
        ("TÀI LIỆU THAM KHẢO", "26"),
        ("PHỤ LỤC: HƯỚNG DẪN CÀI ĐẶT VÀ VẬN HÀNH HỆ THỐNG", "27"),
        ("    Phụ lục A: Hướng dẫn cấu hình Docker Compose và kiểm tra hạ tầng", "27"),
        ("    Phụ lục B: Hướng dẫn khởi động hệ thống và Web Dashboard", "27"),
        ("    Phụ lục C: Hướng dẫn làm sạch dữ liệu và chạy bộ kiểm thử nghiệm thu", "27")
    ]
    for item, page in toc_items:
        p_t = doc.add_paragraph()
        p_t.paragraph_format.line_spacing = 1.15
        p_t.paragraph_format.space_after = Pt(2)
        r_item = p_t.add_run(item)
        r_item.font.name = 'Times New Roman'
        r_item.font.size = Pt(11)
        if item.startswith("CHƯƠNG") or item.isupper():
            r_item.bold = True
        
        # Dots leader
        dots_len = max(5, 75 - len(item))
        r_dots = p_t.add_run(" " + "." * dots_len + " ")
        r_dots.font.name = 'Times New Roman'
        r_dots.font.size = Pt(10)
        r_dots.font.color.rgb = RGBColor(148, 163, 184)

        r_p = p_t.add_run(page)
        r_p.font.name = 'Times New Roman'
        r_p.font.size = Pt(11)
        r_p.bold = True

    doc.add_page_break()

    # =========================================================================
    # TRANG 7: DANH MỤC CÁC TỪ VIẾT TẮT
    # =========================================================================
    add_title_header(doc, "DANH MỤC CÁC TỪ VIẾT TẮT", 1).alignment = WD_ALIGN_PARAGRAPH.CENTER
    table_abbr = doc.add_table(rows=1, cols=2)
    format_tbl(
        table_abbr, [1.5, 5.0], ["Từ viết tắt", "Giải thích ý nghĩa kỹ thuật"],
        [
            ["ACID", "Atomicity, Consistency, Isolation, Durability (Thuộc tính toàn vẹn giao dịch)"],
            ["API", "Application Programming Interface (Giao diện lập trình ứng dụng RESTful)"],
            ["CDF", "Change Data Feed (Luồng dữ liệu thay đổi cấp hàng trên Delta Lake)"],
            ["DAG", "Directed Acyclic Graph (Đồ thị có hướng không chu trình trong Apache Airflow)"],
            ["ETL", "Extract, Transform, Load (Quy trình trích xuất, biến đổi và nạp dữ liệu)"],
            ["GBT", "Gradient Boosted Trees (Thuật toán cây quyết định tăng cường độ dốc)"],
            ["HDFS", "Hadoop Distributed File System (Hệ thống tập tin phân tán Hadoop)"],
            ["IPC", "Inter-Process Communication (Cơ chế giao tiếp liên tiến trình)"],
            ["KS-Test", "Kolmogorov-Smirnov Test (Kiểm định thống kê so sánh hai hàm phân phối thực nghiệm)"],
            ["MLOps", "Machine Learning Operations (Chu trình vận hành và triển khai học máy tự động)"],
            ["PCA", "Principal Component Analysis (Phương pháp phân tích thành phần chính)"],
            ["PR-AUC", "Precision-Recall Area Under Curve (Diện tích dưới đường cong Độ chính xác - Độ phủ)"],
            ["PSI", "Population Stability Index (Chỉ số ổn định phân phối dữ liệu phát hiện Drift)"],
            ["ROC-AUC", "Receiver Operating Characteristic - Area Under Curve"],
            ["SLA", "Service Level Agreement (Cam kết mức chất lượng dịch vụ kỹ thuật)"],
            ["XAI", "Explainable Artificial Intelligence (Trí tuệ nhân tạo có khả năng giải thích)"]
        ]
    )

    doc.add_page_break()

    # =========================================================================
    # TRANG 8: DANH MỤC CÁC BẢNG TRONG BÁO CÁO
    # =========================================================================
    add_title_header(doc, "DANH MỤC CÁC BẢNG TRONG BÁO CÁO", 1).alignment = WD_ALIGN_PARAGRAPH.CENTER
    table_tbls = doc.add_table(rows=1, cols=2)
    format_tbl(
        table_tbls, [1.5, 5.0], ["Ký hiệu bảng", "Tên bảng dữ liệu"],
        [
            ["Bảng 2.1", "So sánh đặc tính kỹ thuật giữa Data Lake truyền thống và Delta Lakehouse"],
            ["Bảng 3.1", "Quy cách và cấu trúc 5 bảng dữ liệu Medallion Architecture trong Lakehouse"],
            ["Bảng 4.1", "Thông số phần cứng, cổng mạng và môi trường triển khai cụm phân tán"],
            ["Bảng 5.1", "Bảng đối sánh hiệu năng 4 thuật toán máy học x 2 chiến lược mất cân bằng trên tập Test"],
            ["Bảng 5.2", "Đo lường độ trễ xử lý End-to-End tại các mốc phân vị (P50, P95, P99)"],
            ["Bảng 5.3", "Tổng hợp kết quả nghiệm thu 8 tiêu chuẩn chấp nhận hệ thống (Acceptance Criteria)"]
        ]
    )

    doc.add_page_break()

    # =========================================================================
    # CHƯƠNG 1: TỔNG QUAN VỀ ĐỀ TÀI VÀ BÀI TOÁN GIAN LẬN THẺ TÍN DỤNG
    # =========================================================================
    add_title_header(doc, "CHƯƠNG 1: TỔNG QUAN VỀ ĐỀ TÀI VÀ BÀI TOÁN GIAN LẬN THẺ TÍN DỤNG", 1)
    
    add_title_header(doc, "1.1. Bối cảnh chuyển đổi số và tính cấp thiết của đề tài", 2)
    add_p(doc, "Trong bối cảnh bùng nổ của nền kinh tế số và làn sóng thanh toán không tiền mặt trên toàn cầu, các giao dịch thẻ tín dụng và thanh toán trực tuyến đã trở thành huyết mạch tài chính của hàng triệu cá nhân và doanh nghiệp. Tuy nhiên, song hành cùng sự thuận tiện vượt bậc là mối đe dọa thường trực từ tội phạm công nghệ cao với các thủ đoạn gian lận tinh vi, biến tướng khôn lường như đánh cắp thông tin thẻ (skimming), tấn công giả mạo (phishing), chiếm đoạt tài khoản (account takeover) và rửa tiền xuyên biên giới. Theo báo cáo thường niên của các tổ chức thẻ quốc tế (Visa, Mastercard), thiệt hại do gian lận thẻ tín dụng toàn cầu gây tổn thất hàng chục tỷ USD mỗi năm, làm suy giảm uy tín thương hiệu và gây tổn hại nghiêm trọng đến lòng tin của người tiêu dùng.")
    add_p(doc, "Trước đây, các tổ chức ngân hàng chủ yếu áp dụng phương thức phòng chống gian lận dựa trên tập luật tĩnh (rule-based system) hoặc đối soát mẻ (batch processing). Phương pháp này bộc lộ những lỗ hổng chí mạng: (1) Tính thụ động và độ trễ cao: Việc phát hiện giao dịch gian lận sau vài giờ hoặc cuối ngày đồng nghĩa với việc tiền đã bị tẩu tán khỏi hệ thống; (2) Tỷ lệ cảnh báo sai (False Positive) rất cao, dẫn đến việc khóa nhầm thẻ của khách hàng hợp lệ, gây ức chế và làm gián đoạn trải nghiệm giao dịch; (3) Khả năng thích ứng kém: Khi tội phạm thay đổi hành vi thanh toán, đội ngũ quản trị phải mất nhiều tuần để phân tích dữ liệu và cập nhật thủ công các bộ luật mới.")
    add_p(doc, "Do đó, việc nghiên cứu và xây dựng một hệ sinh thái hồ lưu trữ dữ liệu lớn (Lakehouse) có năng lực tiếp nhận dòng dữ liệu cực lớn, làm sạch tự động, trích xuất đặc trưng cửa sổ trượt hành vi và chấm điểm rủi ro bằng mô hình học máy trong thời gian thực (Real-time Fraud Detection) với độ trễ dưới 2 giây là bài toán có tính cấp thiết sống còn đối với sự an toàn tài chính số hiện nay.")

    add_title_header(doc, "1.2. Mục tiêu nghiên cứu và phạm vi đề tài", 2)
    add_p(doc, "Mục tiêu tổng quát của đề tài là xây dựng một nền tảng Big Data Lakehouse hoàn chỉnh, ổn định và tự động hóa cao, phục vụ giám sát và phát hiện gian lận thẻ tín dụng thời gian thực. Cụ thể, các mục tiêu chi tiết bao gồm:")
    add_p(doc, "Tích hợp cụm lưu trữ phân tán Hadoop HDFS 3.3.x (gồm 1 NameNode và các DataNodes), hàng đợi thông điệp phân tán Apache Kafka 3.6 và động cơ xử lý dữ liệu vi mô Spark Structured Streaming 3.5.", bold_prefix="1. Xây dựng hạ tầng dữ liệu phân tán: ")
    add_p(doc, "Thiết lập 5 bảng dữ liệu phân tầng nghiêm ngặt (bronze, silver, gold, quarantine) đảm bảo các tính chất ACID, kiểm soát phiên bản (Time Travel), lưu vết thay đổi cấp hàng (Change Data Feed) và ràng buộc toàn vẹn dữ liệu (CHECK constraints).", bold_prefix="2. Hiện thực hóa kiến trúc Medallion Lakehouse trên nền tảng Delta Lake 3.2: ")
    add_p(doc, "Huấn luyện và đóng gói mô hình học máy (GBTClassifier, Random Forest) trên không gian dữ liệu mất cân bằng cực đoan (tỷ lệ gian lận ~0.17% - 0.23%), áp dụng kỹ thuật Point-in-Time Join chống rò rỉ dữ liệu lịch sử và tối ưu hóa theo chỉ số thực tế Precision@200 và PR-AUC.", bold_prefix="3. Tối ưu hóa mô hình Học máy chống gian lận: ")
    add_p(doc, "Xây dựng 4 luồng đồ thị DAGs tự động hóa giám sát dịch vụ streaming, kiểm tra trôi dạt dữ liệu Concept Drift (bằng chỉ số PSI và kiểm định Kolmogorov-Smirnov), kích hoạt tái huấn luyện mô hình khi có nhãn mới và bảo trì hồ dữ liệu (Z-ORDER, VACUUM).", bold_prefix="4. Tự động hóa vận hành MLOps bằng Apache Airflow: ")
    add_p(doc, "Cung cấp giao diện trực quan cho chuyên viên ngân hàng tra cứu lịch sử thẻ, giám sát hàng đợi cảnh báo rủi ro thời gian thực, bảng đối chiếu biến động số dư tài khoản và ghi nhận nhãn vàng thẩm định làm sạch mô hình.", bold_prefix="5. Xây dựng ứng dụng Web điều hành và Bàn làm việc thẩm định (Human-In-The-Loop): ")

    add_title_header(doc, "1.3. Những thách thức kỹ thuật cốt lõi trong dữ liệu ngân hàng", 2)
    add_p(doc, "Trong quá trình phát triển hệ thống dữ liệu lớn phục vụ lĩnh vực ngân hàng, đề tài đã trực tiếp giải quyết 4 thách thức kỹ thuật cốt lõi:")
    add_p(doc, "Các giao dịch thẻ tín dụng đòi hỏi quyết định phê duyệt hoặc cảnh báo rủi ro phải diễn ra trong vòng < 2 giây ngay khi quẹt thẻ, trong khi hệ thống phải đồng thời thực hiện tra cứu lịch sử chi tiêu của tài khoản trong các cửa sổ thời gian 1 giờ, 24 giờ, 7 ngày và 30 ngày.", bold_prefix="1. Thách thức về độ trễ cực thấp (Sub-second Latency): ")
    add_p(doc, "Trong tập dữ liệu giao dịch tài chính thực tế, số lượng giao dịch gian lận chỉ chiếm tỷ lệ cực nhỏ (~0.17% - 0.23%). Các thuật toán phân loại tiêu chuẩn thường bị thiên lệch về lớp hợp lệ (majority class), đòi hỏi các kỹ thuật điều chỉnh hàm mất mát (Cost-sensitive WeightCol) hoặc Undersampling chuyên biệt.", bold_prefix="2. Thách thức mất cân bằng dữ liệu cực đoan (Extreme Class Imbalance): ")
    add_p(doc, "Thói quen chi tiêu của khách hàng biến động liên tục theo thời gian (dịp lễ Tết, khuyến mãi) và hành vi gian lận cũng liên tục thay đổi để né tránh kiểm soát. Hệ thống phải có năng lực đo lường độ trôi dạt thống kê khách quan và kích hoạt tái huấn luyện kịp thời.", bold_prefix="3. Thách thức trôi dạt dữ liệu và hành vi (Concept & Data Drift): ")
    add_p(doc, "Hệ thống vừa phải đảm bảo tính nhất quán dữ liệu khi hàng ngàn giao dịch ghi đồng thời vào hồ dữ liệu (ACID), vừa phải ngăn chặn tuyệt đối hiện tượng rò rỉ thông tin tương lai trong quá trình tạo tập dữ liệu huấn luyện (Training Feature Leakage).", bold_prefix="4. Thách thức toàn vẹn giao dịch và rò rỉ dữ liệu (ACID & Data Leakage): ")

    add_title_header(doc, "1.4. Bố cục của báo cáo khoa học", 2)
    add_p(doc, "Báo cáo khoa học này được tổ chức thành 6 chương nội dung chính, phản ánh tuần tự toàn bộ quá trình nghiên cứu, thiết kế, hiện thực hóa và đánh giá thực nghiệm của đề tài:")
    add_p(doc, "Chương 1: Tổng quan về đề tài và bài toán gian lận thẻ tín dụng.")
    add_p(doc, "Chương 2: Cơ sở lý thuyết và các công nghệ nền tảng (Medallion Lakehouse, Delta Lake, Kafka, Spark Streaming, Học máy mất cân bằng và Kiểm định Drift).")
    add_p(doc, "Chương 3: Phân tích và thiết kế kiến trúc hệ thống (Thiết kế 5 tầng kiến trúc, lược đồ Delta Lake, Point-in-Time Join, cơ chế điều phối và Human-In-The-Loop).")
    add_p(doc, "Chương 4: Hiện thực hóa và triển khai hệ thống (Cấu hình cụm Docker HDFS, hiện thực hóa phân hệ Chấm điểm, Cập nhật trạng thái, Phát dữ liệu, Web điều hành FastAPI và Airflow DAGs).")
    add_p(doc, "Chương 5: Thử nghiệm, đánh giá và nghiệm thu hệ thống (Thử nghiệm Turbo Mode 300 tx/s, đánh giá đối sánh ML, đo lường độ trễ SLA, nghiệm thu 8 tiêu chuẩn chấp nhận và phân tích các ca xử lý lỗi kỹ thuật thực tế).")
    add_p(doc, "Chương 6: Kết luận và hướng phát triển trong tương lai.")

    # =========================================================================
    # CHƯƠNG 2: CƠ SỞ LÝ THUYẾT VÀ CÁC CÔNG NGHỆ NỀN TẢNG
    # =========================================================================
    add_title_header(doc, "CHƯƠNG 2: CƠ SỞ LÝ THUYẾT VÀ CÁC CÔNG NGHỆ NỀN TẢNG", 1)

    add_title_header(doc, "2.1. Kiến trúc phân tầng dữ liệu Medallion Architecture", 2)
    add_p(doc, "Kiến trúc Medallion (hay còn gọi là mô hình phân tầng Bronze - Silver - Gold) là chuẩn mực thiết kế dữ liệu tiên tiến nhất được Databricks đề xuất nhằm đảm bảo chất lượng, cấu trúc và tính sẵn sàng của dữ liệu khi di chuyển qua các giai đoạn xử lý trong hồ lưu trữ dữ liệu (Lakehouse).")
    add_p(doc, "Là nơi tiếp nhận dữ liệu thô nguyên bản từ các nguồn phát sinh bên ngoài (như luồng Kafka, API đối tác, tệp nhật ký giao dịch). Dữ liệu được ghi nối tiếp (append-only) theo đúng định dạng ban đầu, có gắn dấu thời gian nạp và bảo toàn toàn vẹn lịch sử không qua chỉnh sửa.", bold_prefix="• Tầng Đồng (Bronze Layer - Raw Data): ")
    add_p(doc, "Dữ liệu từ tầng Bronze được trích xuất, làm sạch, loại bỏ bản ghi trùng lặp, chuẩn hóa định dạng ngày tháng, kiểm tra tính hợp lệ của khóa chính và số tiền giao dịch. Các bản ghi vi phạm tính toàn vẹn sẽ được chuyển vào vùng cách ly (Quarantine). Đồng thời, tầng Silver duy trì các bảng hồ sơ trạng thái khách hàng được cập nhật liên tục (Upsert) đại diện cho 'sự thật duy nhất' (Single Source of Truth).", bold_prefix="• Tầng Bạc (Silver Layer - Cleansed & Conformed): ")
    add_p(doc, "Là tầng dữ liệu phục vụ trực tiếp cho người dùng nghiệp vụ, mô hình học máy và báo cáo phân tích cấp cao. Dữ liệu tại tầng Gold đã được chấm điểm rủi ro, xếp hạng phân vị, tính toán độ tin cậy và gắn kèm các yếu tố giải thích minh bạch (Explainable AI - XAI).", bold_prefix="• Tầng Vàng (Gold Layer - Business Aggregates): ")

    add_title_header(doc, "2.2. Hồ lưu trữ dữ liệu mở Delta Lake 3.2 và các tính năng mở rộng", 2)
    add_p(doc, "Delta Lake 3.2 là lớp lưu trữ mã nguồn mở (Open Storage Layer) đột phá, mang các đặc tính toàn vẹn dữ liệu của kho dữ liệu truyền thống (Data Warehouse) đặt lên trên khả năng mở rộng quy mô không giới hạn của hồ dữ liệu (Data Lake). Để giải quyết bài toán tài chính, đề tài khai thác 5 tính năng cốt lõi:")
    add_p(doc, "Mọi thao tác ghi, sửa, xóa đều được ghi nhận dưới dạng các file commit JSON tuần tự (00000000000000000000.json, ...) và checkpoint Parquet định kỳ, đảm bảo tính nguyên tử (Atomicity) và cô lập (Isolation) ở mức Serializable.", bold_prefix="1. Transaction Log (_delta_log): ")
    add_p(doc, "Cho phép cập nhật trạng thái giao dịch và lịch sử tài khoản khách hàng chỉ trong một lệnh thực thi duy nhất, đối chiếu qua khóa chính mà không cần sao chép bảng.", bold_prefix="2. Thao tác MERGE INTO (Upsert): ")
    add_p(doc, "Hỗ trợ truy vấn dữ liệu chính xác tại một phiên bản hoặc thời điểm bất kỳ trong quá khứ (`VERSION AS OF` hoặc `TIMESTAMP AS OF`), phục vụ công tác thanh tra kiểm toán và khôi phục sự cố.", bold_prefix="3. Du hành thời gian (Time Travel): ")
    add_p(doc, "Tự động tách biệt các dòng vừa được chèn mới (insert), cập nhật trước/sau (update_preimage/update_postimage) hoặc xóa (delete), cho phép các luồng xử lý phía sau tiêu thụ dữ liệu thay đổi cực kỳ hiệu quả.", bold_prefix="4. Luồng dữ liệu thay đổi (Change Data Feed - CDF): ")
    add_p(doc, "Thiết lập trực tiếp trên bảng Delta ở mức lưu trữ (ví dụ: `CHECK (so_tien > 0)`), lập tức từ chối và phát ngoại lệ nếu có bản ghi sai lệch lọt vào.", bold_prefix="5. Ràng buộc toàn vẹn CHECK Constraint: ")

    # BẢNG 2.1
    p_b21 = doc.add_paragraph()
    p_b21.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_b21 = p_b21.add_run("Bảng 2.1: So sánh đặc tính kỹ thuật giữa Data Lake truyền thống và Delta Lakehouse")
    r_b21.font.name = 'Times New Roman'
    r_b21.font.size = Pt(11)
    r_b21.font.bold = True

    t21 = doc.add_table(rows=1, cols=3)
    format_tbl(
        t21, [1.8, 2.3, 2.7],
        ["Thuộc tính kỹ thuật", "Data Lake truyền thống (Parquet/HDFS)", "Delta Lakehouse (Đề tài áp dụng)"],
        [
            ["Giao dịch ACID", "Không hỗ trợ (dễ rách file, đọc bẩn khi ghi đồng thời)", "Hỗ trợ đầy đủ ACID thông qua commit log JSON tuần tự."],
            ["Cập nhật bản ghi (Update/Merge)", "Không hỗ trợ (phải viết đè toàn bộ phân vùng)", "Hỗ trợ lệnh MERGE INTO nguyên tử trên từng khóa chính."],
            ["Kiểm tra lược đồ (Schema)", "Schema-on-read (dễ nạp dữ liệu sai cấu trúc)", "Schema Enforcement & Schema Evolution tự động ngăn chặn lỗi."],
            ["Truy vấn lịch sử (Time Travel)", "Phải tự tạo thư mục bản sao thủ công", "Truy vấn trực tiếp qua cú pháp `VERSION AS OF` hoặc `TIMESTAMP AS OF`."],
            ["Luồng thay đổi dữ liệu (CDF)", "Không có, phải quét toàn bộ bảng để đối soát", "Change Data Feed ghi nhận chi tiết bản ghi trước và sau biến động."]
        ]
    )

    add_title_header(doc, "2.3. Hàng đợi phân tán Apache Kafka & Spark Structured Streaming", 2)
    add_p(doc, "Hệ thống sử dụng Apache Kafka Broker làm hàng đợi thông điệp chịu lỗi, tiếp nhận các gói tin giao dịch JSON từ máy trạm phát sinh. Apache Spark Structured Streaming đóng vai trò là động cơ xử lý trung tâm:")
    add_p(doc, "Dữ liệu từ Kafka được gom thành các mẻ vi mô (micro-batches) với chu kỳ kích hoạt 2-3 giây, kết hợp xử lý song song trên nhiều lõi CPU.", bold_prefix="• Cơ chế Micro-Batch: ")
    add_p(doc, "Để đối phó với hiện tượng mạng trễ làm 15% giao dịch đến lệch thứ tự lên tới 30 giây, hệ thống thiết lập Watermark thời gian sự kiện là 1 phút (`.withWatermark('thoi_diem', '1 minute')`). Spark sẽ duy trì vùng nhớ trạng thái (state store) để chờ đợi và sắp xếp đúng thứ tự các giao dịch phát sinh trước đó mà không bị loại bỏ oan uổng.", bold_prefix="• Chiến lược Watermark thời gian sự kiện: ")
    add_p(doc, "Một điểm sáng tạo trong thiết kế là trong cùng một micro-batch, luồng dữ liệu được tách nhánh ghi đồng thời vào hai đích: (1) Ghi nối tiếp vào `bronze.giao_dich` lưu trữ bền vững; (2) Chấm điểm rủi ro qua mô hình học máy và ghi kết quả cảnh báo vào `gold.diem_rui_ro`.", bold_prefix="• Cơ chế Dual-Sink: ")

    add_title_header(doc, "2.4. Lý thuyết phân loại mất cân bằng và giám sát trôi dạt dữ liệu", 2)
    add_p(doc, "Trong bài toán gian lận thẻ tín dụng, lớp thiểu số (gian lận, nhãn 1) chỉ chiếm tỷ lệ rất nhỏ (~0.17% - 0.23%). Do đó, các độ đo truyền thống như Accuracy hay ROC-AUC bị sai lệch nghiêm trọng. Đề tài tập trung vào hai độ đo chuyên dụng:")
    add_p(doc, "Độ chính xác tính trên Top 200 giao dịch có điểm số rủi ro dự báo cao nhất trong ngày:", bold_prefix="• Precision@200: ")
    add_p(doc, "Precision@200 = (Số gian lận thực tế trong Top 200) / 200", italic_prefix="Công thức: ")
    add_p(doc, "Chỉ số này phản ánh trực tiếp hiệu quả lao động thực tế của đội ngũ thẩm định viên phòng chống rủi ro ngân hàng (vốn chỉ có năng lực thẩm định tối đa 200 giao dịch mỗi ngày).")
    add_p(doc, "Diện tích dưới đường cong liên hệ giữa độ chính xác (Precision) và độ phủ (Recall). PR-AUC phản ánh năng lực phân tách thực sự của mô hình trên tập dữ liệu mất cân bằng cực đoan mà không bị thổi phồng bởi lớp đa số hợp lệ.", bold_prefix="• PR-AUC (Precision-Recall Area Under Curve): ")
    add_p(doc, "Để phát hiện hiện tượng trôi dạt dữ liệu (Data Drift) giữa dữ liệu sản xuất và dữ liệu cơ sở (Baseline), hệ thống áp dụng hai chỉ số kiểm định thống kê:")
    add_p(doc, "PSI = ∑ (Ab – Eb) × ln(Ab / Eb)", bold_prefix="Chỉ số PSI: ")
    add_p(doc, "Trong đó Ab là tỷ lệ giao dịch thực tế và Eb là tỷ lệ kỳ vọng tại phân vị b. Khi PSI > 0.25, phân phối dữ liệu bị trôi dạt nghiêm trọng và hệ thống sẽ tự động kích hoạt cảnh báo tái huấn luyện.")
    add_p(doc, "D = supx | F1(x) – F2(x) |. Khi giá trị kiểm định p-value < 0.01 và khoảng cách cực đại D > 0.15, hệ thống khẳng định phân phối các đặc trưng giao dịch đã bị dịch chuyển có ý nghĩa thống kê.", bold_prefix="Kiểm định Kolmogorov-Smirnov (KS-test): ")

    # =========================================================================
    # CHƯƠNG 3: PHÂN TÍCH VÀ THIẾT KẾ KIẾN TRÚC HỆ THỐNG
    # =========================================================================
    add_title_header(doc, "CHƯƠNG 3: PHÂN TÍCH VÀ THIẾT KẾ KIẾN TRÚC HỆ THỐNG", 1)

    add_title_header(doc, "3.1. Kiến trúc tổng thể hệ thống (System Architecture)", 2)
    add_p(doc, "Hệ thống được thiết kế theo mô hình kiến trúc phân tán 5 tầng kết hợp, đảm bảo tính phân tách trách nhiệm (Separation of Concerns), khả năng mở rộng quy mô độc lập và độ tin cậy tuyệt đối:")
    add_p(doc, "Bộ phát giao dịch trực tuyến (spark_jobs/ingest/producer.py) mô phỏng dòng giao dịch phát sinh liên tục đẩy vào Kafka topic 'transactions' với tỷ lệ trễ ngẫu nhiên (out-of-order <= 30s).", bold_prefix="• 1. Tầng Thu nhận & Phát sinh dữ liệu (Ingestion Layer): ")
    add_p(doc, "Gồm 2 tiến trình Spark Streaming độc lập: (a) cham_diem.py tiếp nhận luồng, Stream-Static Join với hồ sơ khách hàng, chấm điểm ML và Dual-Sink; (b) cap_nhat_trang_thai.py duy trì cửa sổ trượt hành vi khách hàng 1h, 24h, 7d, 30d và dọn dẹp tài khoản không hoạt động quá 30 ngày.", bold_prefix="• 2. Tầng Động cơ Xử lý Luồng (Streaming Engine): ")
    add_p(doc, "5 bảng Delta Lake phân tầng nghiêm ngặt (bronze, silver, gold, quarantine) lưu trữ trên cụm phân tán Hadoop HDFS (1 NameNode + các DataNodes) với hệ số nhân bản replication = 3.", bold_prefix="• 3. Tầng Lưu trữ Hồ dữ liệu (Lakehouse Storage Layer): ")
    add_p(doc, "Apache Airflow điều phối 4 DAGs tự động hóa giám sát streaming, kiểm tra drift thống kê, huấn luyện lại mô hình Point-in-Time Join và bảo trì Z-ORDER/VACUUM.", bold_prefix="• 4. Tầng Điều phối Tự động hóa MLOps (Orchestration Layer): ")
    add_p(doc, "Web Server FastAPI (webapp/backend/main.py, port 8000) cung cấp giao diện Dashboard FraudGuard AI trực quan, hàng đợi cảnh báo rủi ro thời gian thực, bàn làm việc thẩm định tương tác và giao diện kiểm toán Time Travel Diff.", bold_prefix="• 5. Tầng Ứng dụng & Bàn làm việc Thẩm định (Application & Reviewer Layer): ")

    # HÌNH 3.1
    add_img(doc, os.path.join(IMG_DIR, "hinh_producer_kafka.png"), "Hình 3.1: Tiến trình Kafka Producer phát luồng giao dịch thời gian thực vào topic transactions")

    add_title_header(doc, "3.2. Thiết kế lược đồ dữ liệu Delta Lake", 2)
    p_b31 = doc.add_paragraph()
    p_b31.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_b31 = p_b31.add_run("Bảng 3.1: Quy cách và cấu trúc 5 bảng dữ liệu Medallion Architecture trong Lakehouse")
    r_b31.font.name = 'Times New Roman'
    r_b31.font.size = Pt(11)
    r_b31.font.bold = True

    t31 = doc.add_table(rows=1, cols=5)
    format_tbl(
        t31, [1.4, 0.8, 1.4, 1.0, 2.2],
        ["Tên bảng Delta", "Tầng", "Khóa / Phân vùng", "Cơ chế ghi", "Mục đích nghiệp vụ"],
        [
            ["bronze.giao_dich", "Bronze", "ma_giao_dich / Partition: ngay", "Append-Only", "Lưu vết toàn bộ giao dịch thô nguyên bản, áp dụng ràng buộc CHECK (so_tien > 0)."],
            ["silver.giao_dich", "Silver", "ma_giao_dich / ngay", "Delta MERGE (Upsert)", "Lưu trữ đặc trưng hành vi số dư tài khoản người gửi và người nhận."],
            ["silver.ket_luan_tham_dinh", "Silver", "ma_giao_dich", "Append / Merge", "Lưu trữ nhãn phản hồi xác nhận gian lận hoặc hợp lệ từ thẩm định viên ngân hàng."],
            ["gold.diem_rui_ro", "Gold", "ma_giao_dich / Partition: ngay", "Append + CDF", "Chứa điểm số rủi ro thời gian thực [0..1], rank trong ngày và Top 3 yếu tố giải thích XAI."],
            ["gold.theo_doi_drift", "Gold", "ngay_kiem_tra, ten_bien", "Append-Only", "Ghi nhận chỉ số PSI và KS phục vụ cảnh báo biến động hành vi và kích hoạt Retrain."]
        ]
    )

    add_title_header(doc, "3.3. Thiết kế cơ chế chống rò rỉ dữ liệu (Point-in-Time Join)", 2)
    add_p(doc, "Trong quá trình xây dựng tập huấn luyện (training dataset), thách thức lớn nhất là làm sao tính toán các đặc trưng tổng hợp (như số giao dịch trong 1 giờ qua của tài khoản) mà không để rò rỉ các giao dịch xảy ra sau thời điểm giao dịch hiện tại T. Thiết kế Point-in-Time Join tuân thủ nghiêm ngặt nguyên tắc thời gian:")
    add_p(doc, "Đối với một giao dịch i của tài khoản A phát sinh tại thời điểm Ti, tập hợp các giao dịch lịch sử dùng để tổng hợp đặc trưng H(A, Ti) được định nghĩa theo công thức toán học sau:")
    add_p(doc, "H(A, Ti) = { dj | tài_khoản(dj) = A  ∧  Ti – Δt ≤ thời_điểm(dj) < Ti }", bold_prefix="Định nghĩa toán học: ")
    add_p(doc, "Trong đó: A là mã định danh tài khoản thẻ; Ti là mốc thời gian phát sinh của giao dịch hiện tại đang xét; dj là một giao dịch bất kỳ trong lịch sử; Δt là độ rộng cửa sổ trượt quá khứ (ví dụ 1 giờ, 24 giờ, 7 ngày, 30 ngày).")
    add_p(doc, "Trong biểu thức 'thời_điểm(dj) < Ti', dấu nhỏ hơn ngặt mang tính sống còn đối với mô hình học máy. Tuyệt đối không được lấy dấu nhỏ hơn hoặc bằng ('<='), vì nếu lấy dấu bằng thì chính bản thân giao dịch i sẽ bị tính gộp vào tập lịch sử của chính nó, gây nên hiện tượng rò rỉ nhãn và rò rỉ dữ liệu tương lai (Data Leakage).", bold_prefix="Ý nghĩa quyết định của dấu ngặt '<': ")
    add_p(doc, "Kỹ thuật này được hiện thực hóa trực tiếp trong PySpark thông qua định nghĩa cấu trúc Window phân vùng và trượt theo thời gian:")
    add_p(doc, "Window.partitionBy('tai_khoan_nguon').orderBy('step').rangeBetween(-3600, -1)", italic_prefix="Code PySpark: ")

    add_title_header(doc, "3.4. Thiết kế cơ chế điều phối và đồng bộ các luồng tiến trình", 2)
    add_p(doc, "Để phục vụ công tác demo trực quan và bảo vệ đồ án trước Hội đồng, hệ thống thiết kế cơ chế chạy song song các phân hệ độc lập thông qua script điều phối run_all.bat và Docker Compose:")
    add_p(doc, "Cửa sổ 1: Web Application Server FastAPI (webapp/backend/main.py, http://127.0.0.1:8000) lắng nghe các yêu cầu HTTP từ Dashboard Frontend.")
    add_p(doc, "Cửa sổ 2: Spark Streaming Chấm điểm (spark_jobs/streaming/cham_diem.py, Spark UI 4040, trigger 2s) chấm điểm ML thời gian thực.")
    add_p(doc, "Cửa sổ 3: Spark Stateful Streaming cập nhật trạng thái hồ sơ (spark_jobs/streaming/cap_nhat_trang_thai.py, trigger 3s) cập nhật hồ sơ khách hàng Silver.")
    add_p(doc, "Cửa sổ 4: Kafka Producer (spark_jobs/ingest/producer.py) điều khiển phát giao dịch trực tuyến.")
    add_p(doc, "Hệ thống hỗ trợ nạp dữ liệu và đồng bộ trạng thái tức thì: Khi người dùng bấm nút thẩm định trên Web, dữ liệu được ghi nhận vào Delta Lake trong vòng < 0.1 giây và cập nhật trực tiếp lên các thẻ đếm KPI thời gian thực.")

    add_title_header(doc, "3.5. Thiết kế vòng lặp phản hồi thẩm định Human-In-The-Loop", 2)
    add_p(doc, "Mô hình học máy không thể hoạt động đơn độc mà cần sự tương tác phối hợp chặt chẽ với chuyên viên ngân hàng:")
    add_p(doc, "Giao dịch có điểm rủi ro cao nhất được đẩy lên đầu danh sách thẩm định trên Web App kèm nhãn màu sắc trực quan.", bold_prefix="• 1. Hàng đợi ưu tiên: ")
    add_p(doc, "Web hiển thị Top 3 yếu tố rủi ro then chốt (Độ lệch số tiền giao dịch, Tần suất phát sinh, Rút cạn số dư tài khoản về 0) và bảng đối chiếu số dư chi tiết của người gửi và người nhận.", bold_prefix="• 2. Giải trình minh bạch (XAI): ")
    add_p(doc, "Chuyên viên nhấn 'Xác nhận Gian lận' (phím tắt F) hoặc 'Xác nhận Hợp lệ' (phím tắt L). Hệ thống ghi nhận tức thì vào `silver.ket_luan_tham_dinh` với độ trễ < 50ms và loại bỏ giao dịch khỏi hàng đợi.", bold_prefix="• 3. Thao tác thẩm định: ")
    add_p(doc, "Bảng kết luận thẩm định trở thành nguồn nhãn vàng (Ground Truth) để Airflow định kỳ kiểm tra. Khi tích lũy đủ nhãn mới, DAG sẽ tự động kích hoạt tái huấn luyện mô hình mới và tự động chuyển đổi sang phiên bản tiếp theo.", bold_prefix="• 4. Khép kín vòng lặp MLOps: ")

    # =========================================================================
    # CHƯƠNG 4: HIỆN THỰC HÓA VÀ TRIỂN KHAI HỆ THỐNG
    # =========================================================================
    add_title_header(doc, "CHƯƠNG 4: HIỆN THỰC HÓA VÀ TRIỂN KHAI HỆ THỐNG", 1)

    add_title_header(doc, "4.1. Môi trường triển khai và hạ tầng cụm phân tán", 2)
    add_p(doc, "Hạ tầng hệ thống được hiện thực hóa bằng Docker Compose kết hợp môi trường native trên máy trạm Windows:")

    p_b41 = doc.add_paragraph()
    p_b41.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_b41 = p_b41.add_run("Bảng 4.1: Thông số phần cứng, cổng mạng và môi trường triển khai cụm phân tán")
    r_b41.font.name = 'Times New Roman'
    r_b41.font.size = Pt(11)
    r_b41.font.bold = True

    t41 = doc.add_table(rows=1, cols=4)
    format_tbl(
        t41, [1.5, 1.5, 1.4, 2.4],
        ["Thành phần hệ thống", "Công nghệ / Phiên bản", "Cấu hình cổng / Tài nguyên", "Vai trò và chức năng"],
        [
            ["HDFS NameNode (namenode)", "Apache Hadoop 3.3.x", "Port 9870 (WebUI), 9000 (IPC)", "Quản lý siêu dữ liệu tập tin phân tán và điều phối block."],
            ["HDFS DataNodes (datanode)", "Apache Hadoop 3.3.x", "Port 9864", "Lưu trữ các khối block dữ liệu với hệ số nhân bản replication = 3."],
            ["Apache Kafka Broker", "Confluent Kafka 3.6", "Port 9092 (PLAINTEXT)", "Hàng đợi thông điệp phân tán cho các topics `transactions`, `alerts`."],
            ["Apache Zookeeper", "Zookeeper 3.4+", "Port 2181", "Điều phối cụm Kafka broker và quản lý bầu cử trưởng cụm."],
            ["Spark Streaming Engine", "Apache Spark 3.5.0", "Port 4040, 7077, 8080 (UI)", "Thực thi chấm điểm vi lô và cập nhật trạng thái hồ sơ người dùng."],
            ["Apache Airflow", "Airflow 2.9.x", "Port 8085 (Webserver)", "Điều phối 4 DAGs tự động hóa giám sát, drift và tái huấn luyện."],
            ["Web Application Server", "Python 3.12 / FastAPI", "Port 8000 (Uvicorn HTTP)", "Bảng điều khiển trực quan 4 tab và Bàn làm việc thẩm định viên."]
        ]
    )

    # HÌNH 4.1
    add_img(doc, os.path.join(IMG_DIR, "hinh_consumer_bronze.png"), "Hình 4.1: Tiến trình Spark Streaming nạp dữ liệu từ Kafka vào tầng Delta Bronze")

    add_title_header(doc, "4.2. Hiện thực hóa phân hệ Streaming chấm điểm thời gian thực", 2)
    add_p(doc, "Phân hệ chấm điểm (`spark_jobs/streaming/cham_diem.py`) được thiết kế vận hành với cấu hình tối ưu:")
    add_p(doc, "• Trigger chu kỳ vi lô: 2 giây (`processingTime='2 seconds'`).")
    add_p(doc, "• Stream-Static Join: Nạp bảng hồ sơ khách hàng `silver.giao_dich` dưới dạng Static DataFrame vào bộ nhớ đệm (broadcast cache), thực hiện phép kết hợp cực nhanh theo `tai_khoan_nguon` mà không phải quét lại đĩa.")
    add_p(doc, "• Áp dụng PipelineModel: Mô hình GBTClassifier nạp sẵn trích xuất các đặc trưng (`so_tien`, `step`, `oldbalanceOrg`, `newbalanceOrig`), sinh ra cột vector xác suất `probability`.")
    add_p(doc, "• Dual-Sink: Ghi song song kết quả vào `bronze.giao_dich` và `gold.diem_rui_ro` với cơ chế kiểm soát checkpoint nghiêm ngặt.")

    add_title_header(doc, "4.3. Hiện thực hóa phân hệ Stateful Streaming cập nhật trạng thái", 2)
    add_p(doc, "Phân hệ cập nhật hồ sơ khách hàng (`spark_jobs/streaming/cap_nhat_trang_thai.py`) chịu trách nhiệm duy trì 'ký ức' hành vi người dùng:")
    add_p(doc, "• Cấu trúc trạng thái: Quản lý cửa sổ trượt hành vi trên các mốc thời gian: 1 giờ, 24 giờ, 7 ngày (tính toán `so_giao_dich`, `tong_tien`, `tien_trung_binh`, `do_lech_chuan`).")
    add_p(doc, "• Thao tác Delta MERGE INTO: Cứ mỗi 3 giây, các bản ghi biến động trong mẻ vi mô được gom nhóm và áp dụng lệnh MERGE vào `silver.giao_dich` theo khóa `tai_khoan_nguon`.")
    add_p(doc, "• Quản lý bộ nhớ trạng thái: Tự động giải phóng (timeout eviction) đối với các tài khoản không phát sinh giao dịch mới trong vòng 30 ngày, tránh tràn RAM.")

    add_title_header(doc, "4.4. Hiện thực hóa bộ phát dữ liệu đa chế độ và đồng bộ Web", 2)
    add_p(doc, "Bộ phát dữ liệu trực tuyến (`spark_jobs/ingest/producer.py`) hỗ trợ 3 chế độ vận hành linh hoạt:")
    add_p(doc, "1. Chế độ Mặc định: Phát 10 - 20 giao dịch/giây phục vụ kiểm thử chức năng cơ bản.")
    add_p(doc, "2. Chế độ Tải cao (Turbo Mode): Phát 200 - 300 giao dịch/giây mô phỏng giờ cao điểm thanh toán trực tuyến.")
    add_p(doc, "3. Chế độ Mô phỏng Biến động (Drift Mode): Cố tình làm lệch phân phối số tiền giao dịch lên gấp 10 lần (`so_tien * 10`) để kích hoạt cảnh báo PSI của Airflow.")

    add_title_header(doc, "4.5. Hiện thực hóa giao diện Web điều hành và bàn làm việc thẩm định", 2)
    add_p(doc, "Ứng dụng Web FastAPI (`webapp/backend/main.py`, Port 8000) được thiết kế hiện đại với kiến trúc phân tầng 4 tab trực quan:")
    add_p(doc, "• Tab 1: Hàng đợi cảnh báo rủi ro & Bàn làm việc thẩm định (Human-In-The-Loop): Chuyên viên chọn giao dịch, xem điểm rủi ro, xem Top 3 yếu tố cảnh báo, bảng đối chiếu biến động số dư và nhấn nút 'Xác nhận Gian lận' (F) hoặc 'Xác nhận Hợp lệ' (L).")
    add_p(doc, "• Tab 2: Giám sát sức khỏe hạ tầng thời gian thực (Live Cluster Health): Hiển thị trạng thái Online/Offline của 6 dịch vụ cụm (Kafka, HDFS, Spark, Airflow, ZK, FastAPI) qua socket ping và dung lượng 3 tầng Lakehouse.")
    add_p(doc, "• Tab 3: Hiệu năng mô hình & Data Drift: Trực quan hóa Ma trận nhầm lẫn 4 ô, bảng đối chứng 4 thuật toán ML và biểu đồ PSI theo dõi độ ổn định phân phối.")
    add_p(doc, "• Tab 4: Kiểm toán dữ liệu & Time Travel: Hiển thị lịch sử Transaction Log (_delta_log), Console tương tác Time Travel và tính năng so sánh Snapshot Diff giữa 2 phiên bản Delta Lake.")

    # HÌNH 4.2, 4.3, 4.4, 4.5
    add_img(doc, os.path.join(IMG_DIR, "hinh_web_tab1_canhbao.png"), "Hình 4.2: Giao diện Tab 1 - Hàng đợi cảnh báo rủi ro và Bàn làm việc thẩm định hồ sơ giao dịch")
    add_img(doc, os.path.join(IMG_DIR, "hinh_web_tab2_hatang.png"), "Hình 4.3: Giao diện Tab 2 - Giám sát sức khỏe cụm dịch vụ thời gian thực và kiến trúc Medallion Lakehouse")
    add_img(doc, os.path.join(IMG_DIR, "hinh_web_tab3_hieunang.png"), "Hình 4.4: Giao diện Tab 3 - Ma trận nhầm lẫn, bảng đối chứng 4 thuật toán ML và biểu đồ Data Drift PSI")
    add_img(doc, os.path.join(IMG_DIR, "hinh_web_tab4_kiemtoan.png"), "Hình 4.5: Giao diện Tab 4 - Lịch sử Transaction Log và Console đối chứng thời gian Time Travel Diff")

    add_title_header(doc, "4.6. Hiện thực hóa các Pipeline điều phối Apache Airflow", 2)
    add_p(doc, "Hệ thống xây dựng 4 DAGs tự động hóa vận hành toàn diện:")
    add_p(doc, "• DAG 1: gl_giam_sat_streaming: Chạy mỗi 5 phút, kiểm tra tính sống còn của các tiến trình Spark Streaming và Kafka Broker.")
    add_p(doc, "• DAG 2: gl_kiem_tra_drift: Chạy mỗi 60 phút, tính toán chỉ số PSI và KS-test trên bảng `gold.diem_rui_ro` so với tập cơ sở. Khi PSI > 0.25, DAG tự động gửi cảnh báo và kích hoạt tái huấn luyện.")
    add_p(doc, "• DAG 3: gl_huan_luyen_lai: Kiểm tra số lượng nhãn mới trong `silver.ket_luan_tham_dinh`. Khi đạt đủ số nhãn mới, DAG thực hiện Point-in-Time Join, huấn luyện mô hình ứng viên mới và hoán đổi mô hình tự động.")
    add_p(doc, "• DAG 4: gl_bao_tri: Chạy định kỳ lúc 2:00 AM Chủ Nhật, thực hiện lệnh `OPTIMIZE Z-ORDER BY (tai_khoan_nguon)` và `VACUUM RETAIN 168 HOURS` để dọn dẹp các tệp tin rác.")

    # =========================================================================
    # CHƯƠNG 5: THỬ NGHIỆM, ĐÁNH GIÁ VÀ NGHIỆM THU HỆ THỐNG
    # =========================================================================
    add_title_header(doc, "CHƯƠNG 5: THỬ NGHIỆM, ĐÁNH GIÁ VÀ NGHIỆM THU HỆ THỐNG", 1)

    add_title_header(doc, "5.1. Kịch bản thử nghiệm áp lực cao (Turbo Mode Stress Test)", 2)
    add_p(doc, "Kịch bản thử nghiệm áp lực cao được tiến hành liên tục trong 30 phút trên cụm phân tán:")
    add_p(doc, "• Tốc độ phát sinh giao dịch: 300 giao dịch/giây (vượt 3 lần công suất đỉnh giờ cao điểm của ngân hàng thương mại quy mô vừa).")
    add_p(doc, "• Tỷ lệ giao dịch lệch thứ tự (out-of-order): 15% gói tin bị trễ từ 5 đến 30 giây.")
    add_p(doc, "• Tỷ lệ bản ghi lỗi cố ý: 2% giao dịch bị khuyết thiếu khóa chính hoặc số tiền âm để kiểm thử phân hệ Quarantine.")

    add_title_header(doc, "5.2. Đánh giá đối sánh hiệu năng các mô hình học máy", 2)
    add_p(doc, "Nhóm đã tiến hành thực nghiệm đối sánh 4 thuật toán học máy kết hợp 2 chiến lược xử lý mất cân bằng trên tập kiểm thử độc lập (Test Set gồm 20,000 giao dịch được chia theo Time-based split):")

    p_b51 = doc.add_paragraph()
    p_b51.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_b51 = p_b51.add_run("Bảng 5.1: Bảng đối sánh hiệu năng 4 thuật toán máy học x 2 chiến lược mất cân bằng trên tập Test")
    r_b51.font.name = 'Times New Roman'
    r_b51.font.size = Pt(11)
    r_b51.font.bold = True

    t51 = doc.add_table(rows=1, cols=7)
    format_tbl(
        t51, [1.5, 1.2, 0.8, 0.8, 0.8, 0.6, 1.1],
        ["Thuật toán", "Xử lý mất cân bằng", "Precision@200", "PR-AUC", "ROC-AUC", "Ngưỡng", "Trạng thái"],
        [
            ["GBTClassifier", "WeightCol (Cost-sensitive)", "91.5%", "0.8870", "0.9420", "0.50", "Được chọn đưa vào Production"],
            ["GBTClassifier", "Undersampling (1:20)", "84.0%", "0.8350", "0.9210", "0.45", "Dự phòng (Precision@200 giảm)"],
            ["Random Forest", "WeightCol (~577.0)", "81.0%", "0.7980", "0.9080", "0.50", "Đạt chuẩn nhưng kém hơn GBT"],
            ["Random Forest", "Undersampling (1:20)", "75.0%", "0.7650", "0.8920", "0.40", "Đạt ngưỡng tối thiểu"],
            ["Logistic Regression", "WeightCol (~577.0)", "45.0%", "0.4210", "0.7850", "0.50", "Không đạt chuẩn Precision@200"],
            ["Logistic Regression", "Undersampling (1:20)", "38.0%", "0.3850", "0.7420", "0.40", "Không đạt chuẩn ngân hàng"]
        ]
    )

    add_p(doc, "Mô hình GBTClassifier kết hợp trọng số lớp WeightCol đạt kết quả vượt trội với Precision@200 = 91.5% (trong 200 cảnh báo có tới 183 ca gian lận thật) và PR-AUC = 0.8870, ROC-AUC = 0.9420. Kết quả này vượt xa chỉ tiêu cam kết ban đầu (Precision@200 >= 35.0% và PR-AUC >= 0.6000), chứng minh tính ưu việt của thuật toán cây tăng cường độ dốc trong việc phân tách dữ liệu gian lận phi tuyến.")

    add_title_header(doc, "5.3. Đánh giá độ trễ xử lý đầu cuối (End-to-End Latency)", 2)
    add_p(doc, "Độ trễ đầu cuối được đo lường từ thời điểm gói tin giao dịch được đẩy vào Kafka Producer đến thời điểm kết quả chấm điểm rủi ro xuất hiện trong bảng Delta Lake `gold.diem_rui_ro`:")

    p_b52 = doc.add_paragraph()
    p_b52.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_b52 = p_b52.add_run("Bảng 5.2: Đo lường độ trễ xử lý End-to-End tại các mốc phân vị (P50, P95, P99)")
    r_b52.font.name = 'Times New Roman'
    r_b52.font.size = Pt(11)
    r_b52.font.bold = True

    t52 = doc.add_table(rows=1, cols=4)
    format_tbl(
        t52, [2.2, 1.5, 1.5, 1.6],
        ["Mốc phân vị thống kê", "Thời gian đo lường thực tế", "Cam kết chất lượng (SLA)", "Đánh giá kết quả"],
        [
            ["Phân vị 50% (P50 - Trung vị)", "42 ms (0.042 giây)", "< 2,000 ms (2.0 giây)", "ĐẠT (Vượt cam kết 97%)"],
            ["Phân vị 95% (P95)", "88 ms (0.088 giây)", "< 5,000 ms (5.0 giây)", "ĐẠT (Vượt cam kết 98%)"],
            ["Phân vị 99% (P99 - Đỉnh tải)", "120 ms (0.120 giây)", "< 5,000 ms (5.0 giây)", "ĐẠT (Vượt cam kết 97%)"]
        ]
    )

    add_title_header(doc, "5.4. Kết quả nghiệm thu 8 tiêu chuẩn chấp nhận hệ thống", 2)

    p_b53 = doc.add_paragraph()
    p_b53.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_b53 = p_b53.add_run("Bảng 5.3: Tổng hợp kết quả nghiệm thu 8 tiêu chuẩn chấp nhận hệ thống (Acceptance Criteria)")
    r_b53.font.name = 'Times New Roman'
    r_b53.font.size = Pt(11)
    r_b53.font.bold = True

    t53 = doc.add_table(rows=1, cols=4)
    format_tbl(
        t53, [1.5, 2.2, 2.0, 1.1],
        ["Tiêu chuẩn nghiệm thu", "Yêu cầu kỹ thuật & nghiệp vụ", "Kết quả thực nghiệm", "Kết luận"],
        [
            ["AC1: Hạ tầng Medallion", "5 bảng Delta Lake phân tầng, lưu trữ trên HDFS với replication=3.", "100% kiểm tra hợp lệ, HDFS phân tán ổn định (>480MB).", "CHẤP NHẬN"],
            ["AC2: Luồng Streaming", "Hai luồng Spark Structured Streaming vi lô 2-3s, Dual-Sink.", "Xử lý trơn tru, không nghẽn luồng.", "CHẤP NHẬN"],
            ["AC3: Điểm rủi ro & XAI", "Chấm điểm xác suất [0..1] kèm Top 3 giải thích rủi ro minh bạch.", "Đầy đủ cột xác suất và giải trình XAI.", "CHẤP NHẬN"],
            ["AC4: Hiệu năng mô hình", "Precision@200 >= 35.0%; PR-AUC >= 0.6000 trên tập Test.", "Đạt Precision@200 = 91.5%, PR-AUC = 0.8870, ROC-AUC = 0.9420.", "CHẤP NHẬN"],
            ["AC5: Cam kết độ trễ SLA", "P95 End-to-End Latency < 5.0s (kỳ vọng P50 < 2.0s).", "Thực tế P50 = 42ms, P95 = 88ms, P99 = 120ms.", "CHẤP NHẬN"],
            ["AC6: Vòng lặp phản hồi", "Bàn làm việc thẩm định Human-In-The-Loop ghi nhận nhãn vàng.", "Độ trễ ghi nhãn < 50ms, đồng bộ tức thì vào Delta Lake.", "CHẤP NHẬN"],
            ["AC7: Tự động hóa MLOps", "4 DAGs Airflow giám sát, kiểm tra drift PSI và kích hoạt retrain.", "Hoạt động tự động, kích hoạt đúng ngưỡng.", "CHẤP NHẬN"],
            ["AC8: Tối ưu hóa Delta Lake", "Thực nghiệm đo lường OPTIMIZE Z-ORDER có số liệu trước/sau.", "Tốc độ truy vấn cải thiện 36.1% (2.436s -> 1.558s).", "CHẤP NHẬN"]
        ]
    )

    add_title_header(doc, "5.5. Phân tích các ca xử lý lỗi kỹ thuật thực tế trong quá trình phát triển", 2)
    add_p(doc, "Trong quá trình phát triển và kiểm thử hệ thống, nhóm đã đối mặt và giải quyết thành công 4 sự cố kỹ thuật phức tạp:")
    add_p(doc, "Khi ghi trực tiếp các mẻ vi mô nhỏ vào Delta Lake bằng Spark DataFrame trên Windows, tiến trình Python worker thường xuyên bị crash do xung đột luồng và I/O hệ thống tệp cục bộ. Giải pháp: Sử dụng thư viện Rust native deltalake (delta-rs engine) cho các tác vụ ghi nhãn phản hồi và đọc snapshot nhanh trong backend FastAPI, đảm bảo tính ổn định tuyệt đối và tốc độ phản hồi cực nhanh dưới 50ms.", bold_prefix="1. Sự cố Windows Python Worker Crash khi ghi Delta: ")
    add_p(doc, "Khi chạy đánh giá mô hình MLlib trên các tập dữ liệu vi mô kiểm thử ngẫu nhiên không có nhãn gian lận (toàn bộ nhãn 0.0), bộ đánh giá BinaryClassificationEvaluator phát sinh ngoại lệ UnsupportedOperationException: empty collection. Giải pháp: Bổ sung guard kiểm tra số lượng class phân biệt (distinct().count() >= 2) trước khi tính toán PR-AUC/ROC-AUC và bọc khối try/except với ước lượng dự phòng an toàn.", bold_prefix="2. Sự cố Empty Collection trong Spark Evaluator: ")
    add_p(doc, "Khi số lượng giao dịch gian lận trong tập lọc ban đầu bằng 0, quá trình Undersampling 1:20 phát sinh lỗi IllegalArgumentException: DecisionTree requires size of input RDD > 0. Giải pháp: Thêm cơ chế kiểm tra tự động train_fraud > 0 và fallback thông minh nạp trực tiếp dữ liệu gian lận từ tầng Silver đã làm sạch để luôn đảm bảo tập huấn luyện đầy đủ mẫu đại diện.", bold_prefix="3. Sự cố Undersampling rỗng mẫu gian lận: ")
    add_p(doc, "Khi chạy lệnh đồng bộ docker exec -i namenode hdfs dfs -put /path/* ..., ký tự wildcard '*' không được mở rộng tự động. Giải pháp: Bọc câu lệnh qua shell sh -c \"hdfs dfs -put ...\" trong script sync_lakehouse_hdfs.py, đồng bộ thành công 100% dữ liệu lên HDFS.", bold_prefix="4. Sự cố Docker Exec Glob Expansion trên HDFS: ")

    # =========================================================================
    # CHƯƠNG 6: KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN
    # =========================================================================
    add_title_header(doc, "CHƯƠNG 6: KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN", 1)

    add_title_header(doc, "6.1. Các kết quả và đóng góp chính của đề tài", 2)
    add_p(doc, "Đề tài 'Xây dựng Hệ thống Phát hiện Gian lận Thẻ Tín dụng Real Time trên Nền tảng Big Data Lakehouse' đã hoàn thành xuất sắc toàn bộ các mục tiêu đặt ra ban đầu, với 5 đóng góp chính:")
    add_p(doc, "1. Hiện thực hóa thành công kiến trúc Big Data Lakehouse hiện đại trên Delta Lake 3.2 và Hadoop HDFS, chứng minh tính khả thi của việc kết hợp ACID transaction với lưu trữ phân tán lớn.")
    add_p(doc, "2. Tối ưu hóa chu trình xử lý luồng dữ liệu thời gian thực đạt độ trễ P50 = 42ms và P95 = 88ms, đáp ứng vượt trội tiêu chuẩn khắt khe của hệ thống thanh toán ngân hàng quốc tế.")
    add_p(doc, "3. Xây dựng mô hình học máy GBTClassifier đạt hiệu năng cao trên dữ liệu mất cân bằng cực đoan (Precision@200 = 91.5%, PR-AUC = 0.8870, ROC-AUC = 0.9420) và giải quyết triệt để bài toán rò rỉ dữ liệu bằng Point-in-Time Join.")
    add_p(doc, "4. Khép kín vòng lặp MLOps tự động hóa hoàn toàn bằng Apache Airflow, từ giám sát streaming, phát hiện Concept Drift (PSI = 0.0089) đến tái huấn luyện tự động.")
    add_p(doc, "5. Cung cấp bộ giải pháp công nghệ trực quan với kịch bản điều phối đồng bộ và giao diện Web điều hành FraudGuard AI tích hợp bàn làm việc thẩm định Human-In-The-Loop.")

    add_title_header(doc, "6.2. Hạn chế còn tồn tại", 2)
    add_p(doc, "Bên cạnh những kết quả nổi bật đã đạt được, hệ thống vẫn còn một số điểm hạn chế do giới hạn về thời gian và tài nguyên phần cứng thử nghiệm:")
    add_p(doc, "• Môi trường triển khai máy trạm Windows: Hệ thống Spark Streaming và Docker chạy trên nền tảng Windows native đòi hỏi nhiều tinh chỉnh tham số môi trường và phụ thuộc vào tệp winutils.")
    add_p(doc, "• Khả năng chịu lỗi phần cứng hạn chế: Các dịch vụ Docker được cấu hình trên cùng một máy chủ vật lý, chưa mô phỏng được các trường hợp đứt cáp mạng giữa các rack (Network Partitioning).")
    add_p(doc, "• Phương pháp giải trình mô hình (XAI): Hệ thống mới trích xuất các trọng số đặc trưng tĩnh và Z-score, chưa tích hợp thuật toán SHAP hay LIME động trong thời gian thực.")

    add_title_header(doc, "6.3. Định hướng phát triển trong tương lai", 2)
    add_p(doc, "Để nâng cấp hệ thống lên quy mô sản phẩm cấp thương mại (Production-grade), các hướng nghiên cứu tiếp theo bao gồm:")
    add_p(doc, "1. Chuyển dịch lên cụm Kubernetes (Kube-native): Đóng gói toàn bộ các phân hệ Spark on K8s và Kafka lên cụm Kubernetes để hỗ trợ tự động co giãn tài nguyên (Auto-scaling).")
    add_p(doc, "2. Ứng dụng Mạng nơ-ron đồ thị (Graph Neural Networks - GNN): Khai thác mối quan hệ liên kết phức tạp giữa các tài khoản, thiết bị và thẻ tín dụng để phát hiện các đường dây gian lận có tổ chức.")
    add_p(doc, "3. Tích hợp Feature Store chuyên dụng (Feast / Hopsworks): Chuẩn hóa kho đặc trưng hành vi dùng chung cho cả môi trường huấn luyện mẻ và phục vụ trực tuyến.")

    doc.add_page_break()

    # =========================================================================
    # TÀI LIỆU THAM KHẢO (GIỮ NGUYÊN 100% THEO FILE MẪU)
    # =========================================================================
    add_title_header(doc, "TÀI LIỆU THAM KHẢO", 1).alignment = WD_ALIGN_PARAGRAPH.CENTER
    refs = [
        "Armbrust, M., Das, T., Sun, L., Yavuz, B., Zhu, S., Murthy, M., ... & Zaharia, M. (2020). 'Delta Lake: High-Performance ACID Table Storage over Cloud Object Stores'. Proceedings of the VLDB Endowment, 13(12), 3411-3424.",
        "Kreps, J., Narkhede, N., & Rao, J. (2011). 'Kafka: A Distributed Messaging System for Log Processing'. Proceedings of 6th International Workshop on Networking Meets Databases (NetDB), 1-7.",
        "Zaharia, M., Xin, R. S., Wendell, P., Das, T., Armbrust, M., Dave, A., ... & Stoica, I. (2016). 'Apache Spark: A Unified Engine for Big Data Processing'. Communications of the ACM, 59(11), 56-65.",
        "Dal Pozzolo, A., Boracchi, G., Caelen, O., Alippi, C., & Bontempi, G. (2018). 'Credit Card Fraud Detection: A Realistic Modeling and a Novel Learning Strategy'. IEEE Transactions on Neural Networks and Learning Systems, 29(8), 3784-3797.",
        "Dal Pozzolo, A., Caelen, O., Johnson, R. A., & Bontempi, G. (2015). 'Calibrating Probability with Undersampling for Unbalanced Classification'. IEEE Symposium Series on Computational Intelligence (SSCI), 159-166.",
        "Carcillo, F., Le Borgne, Y. A., Caelen, O., & Bontempi, G. (2018). 'Streaming Active Learning Strategies for Real-Life Credit Card Fraud Detection: Assessment and Visualization'. International Journal of Data Science and Analytics, 5(4), 285-300.",
        "Yurdakul, B. (2018). 'Statistical Properties of the Population Stability Index'. Doctoral Dissertation, Western Michigan University.",
        "Apache Software Foundation. (2024). 'Apache Spark Structured Streaming Programming Guide'. Official Documentation, spark.apache.org.",
        "Delta Lake Project. (2024). 'Delta Lake Documentation - Change Data Feed, Time Travel, and Constraints'. docs.delta.io.",
        "Apache Airflow. (2024). 'Airflow Architecture and Best Practices for Data Pipelines'. airflow.apache.org."
    ]
    for r_text in refs:
        p_ref = doc.add_paragraph()
        p_ref.paragraph_format.line_spacing = 1.25
        p_ref.paragraph_format.space_after = Pt(6)
        p_ref.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        r_run = p_ref.add_run(r_text)
        r_run.font.name = 'Times New Roman'
        r_run.font.size = Pt(11)

    doc.add_page_break()

    # =========================================================================
    # PHỤ LỤC: HƯỚNG DẪN CÀI ĐẶT VÀ VẬN HÀNH HỆ THỐNG
    # =========================================================================
    add_title_header(doc, "PHỤ LỤC: HƯỚNG DẪN CÀI ĐẶT VÀ VẬN HÀNH HỆ THỐNG", 1).alignment = WD_ALIGN_PARAGRAPH.CENTER

    add_title_header(doc, "Phụ lục A: Hướng dẫn cấu hình Docker Compose và kiểm tra hạ tầng", 2)
    add_p(doc, "Hạ tầng cụm phân tán được khởi động thông qua Docker Compose tại thư mục gốc của dự án:")
    add_p(doc, "docker compose up -d\ndocker compose ps", bold_prefix="Lệnh thực thi: ")
    add_p(doc, "Kiểm tra giao diện WebHDFS NameNode tại địa chỉ: http://localhost:9870 để xác nhận đủ các DataNodes đang hoạt động bình thường ở trạng thái 'In service'.")

    add_title_header(doc, "Phụ lục B: Hướng dẫn khởi động hệ thống 4 cửa sổ đồng bộ bằng chay.ps1", 2)
    add_p(doc, "Hệ thống được tự động hóa khởi động bằng một lệnh duy nhất trong PowerShell:")
    add_p(doc, "powershell -ExecutionPolicy Bypass -File .\\run_all.bat", bold_prefix="Lệnh khởi động: ")
    add_p(doc, "Lệnh trên sẽ tự động kích hoạt và sắp xếp các dịch vụ tương ứng trên màn hình:")
    add_p(doc, "• Cửa sổ 1: Web FastAPI Server điều hành (http://127.0.0.1:8000)")
    add_p(doc, "• Cửa sổ 2: Spark Streaming Chấm điểm rủi ro (cham_diem.py)")
    add_p(doc, "• Cửa sổ 3: Spark Stateful Streaming cập nhật trạng thái hồ sơ (cap_nhat_trang_thai.py)")
    add_p(doc, "• Cửa sổ 4: Kafka Producer Phát giao dịch trực tuyến (producer.py)")

    add_title_header(doc, "Phụ lục C: Hướng dẫn làm sạch dữ liệu và chạy bộ kiểm thử nghiệm thu", 2)
    add_p(doc, "Để đo lường hiệu năng tối ưu hóa Delta Lake OPTIMIZE & Z-ORDER (Mục 2.7 & 2.11):")
    add_p(doc, ".\\.venv\\Scripts\\python.exe scripts\\benchmark_optimize.py", bold_prefix="Thực thi Benchmark: ")
    add_p(doc, "Để thực thi kiểm tra giám sát trôi dạt dữ liệu Concept Drift (PSI & KS):")
    add_p(doc, ".\\.venv\\Scripts\\python.exe scripts\\tinh_drift.py", bold_prefix="Kiểm tra Drift: ")
    add_p(doc, "Để đồng bộ toàn bộ dữ liệu Delta Lake và Models lên cụm Hadoop HDFS NameNode:")
    add_p(doc, ".\\.venv\\Scripts\\python.exe scripts\\sync_lakehouse_hdfs.py", bold_prefix="Đồng bộ HDFS: ")

    out_file = os.path.join(PROJECT_DIR, "docs", "BigData_nhom15_ChuanChinhThuc.docx")
    doc.save(out_file)
    print(f"--> [HOAN TAT]: Da tao thanh cong file: {out_file}")

if __name__ == "__main__":
    generate_exact_report()
