STUDENTS = {
    "23T1020001": {
        "name": "Nguyễn Văn An", 
        "lop": "K47A",
        "scores": {"PMMNM": 8.5, "CSDL": 7.0, "MMT": 9.0}
    },
    "23T1020002": {
        "name": "Trần Thị Bình", 
        "lop": "K47A",
        "scores": {"PMMNM": 6.0, "CSDL": 5.5, "MMT": 7.0}
    },
    "23T1020003": {
        "name": "Lê Hoàng Cường", 
        "lop": "K47B",
        "scores": {"PMMNM": 9.5, "CSDL": 9.0}
    },
    "23T1020004": {
        "name": "Phạm Văn Dũng", 
        "lop": "K47B",
        "scores": {"PMMNM": 4.0, "CSDL": 3.5, "MMT": 5.0}
    },
    "23T1020005": {
        "name": "Hoàng Thu Hà", 
        "lop": "K47A",
        "scores": {}
    },
    "23T1020006": {
        "name": "Võ Quốc Khánh", 
        "lop": "K47C",
        "scores": {"PMMNM": 7.5, "MMT": 8.0}
    },
}


from flask import Flask, request, url_for
from markupsafe import escape

app = Flask(__name__)

def tinh_diem_va_xep_loai(scores):
    if not scores:
        return "-", "-"
    
    dtb = sum(scores.values()) / len(scores)
    
    if dtb >= 8.5:
        xep_loai = "Giỏi"
    elif dtb >= 7.0:
        xep_loai = "Khá"
    elif dtb >= 5.0:
        xep_loai = "Trung bình"
    else:
        xep_loai = "Yếu"
        
    return f"{dtb:.2f}", xep_loai

@app.route("/")
def index():
    total_students = len(STUDENTS)

    ds_lop = set(st["lop"] for st in STUDENTS.values())
    total_classes = len(ds_lop)

    students_link = url_for("student_list")
    classes_link = url_for("api_students")

    return f"""
    <h1>Trang chủ Quản lý Sinh viên</h1>
    <hr>
    <h3>Thống kê tổng quan:</h3>
    <ul>
        <li><b>Tổng số sinh viên:</b> {total_students} sinh viên</li>
        <li><b>Tổng số lớp:</b> {total_classes} lớp ({", ".join(sorted(ds_lop))})</li>
    </ul>
    
    <h3>Liên kết điều hướng (được sinh bằng url_for):</h3>
    <ul>
        <li><a href="{students_link}">Xem danh sách sinh viên</a></li>
        <li><a href="{classes_link}">Xem danh sách các lớp</a></li>
    </ul>
    """

@app.route("/students")
def student_list():
    # 1. Lấy tham số 'lop' từ URL (ví dụ: /students?lop=k47a)
    selected_lop = request.args.get("lop", "").strip()
    
    # 2. Tạo thanh lọc danh sách lớp ĐỘNG (không viết cứng)
    danh_sach_lop = sorted(list(set(st["lop"] for st in STUDENTS.values())))
    
    filter_html = f'<a href="{url_for("student_list")}">Tất cả</a>'
    for c in danh_sach_lop:
        # Dùng url_for("student_list", lop=c) để sinh link ?lop=K47A
        filter_html += f' | <a href="{url_for("student_list", lop=c)}">{c}</a>'
        
    # 3. Lặp qua STUDENTS để ghép các hàng <tr> trong bảng
    rows_html = ""
    match_count = 0  # Đếm số sinh viên thỏa mãn bộ lọc
    
    for mssv, info in STUDENTS.items():
        # Kiểm tra lọc theo lớp (không phân biệt hoa thường)
        if selected_lop and info["lop"].lower() != selected_lop.lower():
            continue
            
        match_count += 1
        dtb, xep_loai = tinh_diem_va_xep_loai(info["scores"])
        
        # Tạo đường dẫn liên kết đến trang chi tiết sinh viên
        detail_url = url_for("student_detail", mssv=mssv)
        
        # Cộng dồn hàng HTML
        rows_html += f"""
        <tr>
            <td><a href="{detail_url}">{mssv}</a></td>
            <td>{escape(info['name'])}</td>
            <td>{escape(info['lop'])}</td>
            <td>{dtb}</td>
            <td>{xep_loai}</td>
        </tr>
        """
        
    # 4. Hiển thị thông báo nếu không có kết quả phù hợp
    if match_count == 0:
        table_content = "<p><b>Không có sinh viên phù hợp.</b></p>"
    else:
        table_content = f"""
        <table border="1" cellpadding="8" cellspacing="0">
            <thead>
                <tr>
                    <th>MSSV</th>
                    <th>Họ tên</th>
                    <th>Lớp</th>
                    <th>Điểm TB</th>
                    <th>Xếp loại</th>
                </tr>
            </thead>
            <tbody>
                {rows_html}
            </tbody>
        </table>
        """

    return f"""
    <h1>Bảng thông tin sinh viên</h1>
    <hr>
    <p><b>Lọc theo lớp:</b> {filter_html}</p>
    {table_content}
    <br>
    <p><a href="{url_for('index')}">← Về trang chủ</a></p>
    """

# Trang chi tiết sinh viên (để tạo đường dẫn MSSV)
@app.route("/students/<mssv>")
def student_detail(mssv):
    student = STUDENTS.get(mssv)
    if not student:
        return "Không tìm thấy sinh viên!", 404
    return f"Trang chi tiết của sinh viên: <b>{escape(student['name'])}</b> ({mssv})"

# API sinh viên theo yêu cầu đề bài Câu 1
@app.route("/api/students")
def api_students():
    return STUDENTS

if __name__ == "__main__":
    app.run(debug=True, port=8000)


