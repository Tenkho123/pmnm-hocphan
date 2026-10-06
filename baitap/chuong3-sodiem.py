@ -1,3 +1,8 @@
from flask import Flask, abort, request, url_for, make_response, redirect
from markupsafe import escape

app = Flask(__name__)

STUDENTS = {
    "23T1020001": {
        "name": "Nguyễn Văn An", 
@ -31,12 +36,6 @@ STUDENTS = {
    },
}


from flask import Flask, request, url_for
from markupsafe import escape

app = Flask(__name__)

def tinh_diem_va_xep_loai(scores):
    if not scores:
        return "-", "-"
@ -54,10 +53,11 @@ def tinh_diem_va_xep_loai(scores):
        
    return f"{dtb:.2f}", xep_loai


# ---------------- CÂU 1: TRANG CHỦ ( / ) ----------------
@app.route("/")
def index():
    total_students = len(STUDENTS)

    ds_lop = set(st["lop"] for st in STUDENTS.values())
    total_classes = len(ds_lop)

@ -80,35 +80,28 @@ def index():
    </ul>
    """


# ---------------- CÂU 2: BẢNG DANH SÁCH ( /students ) ----------------
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
    match_count = 0
    
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
@ -119,7 +112,6 @@ def student_list():
        </tr>
        """
        
    # 4. Hiển thị thông báo nếu không có kết quả phù hợp
    if match_count == 0:
        table_content = "<p><b>Không có sinh viên phù hợp.</b></p>"
    else:
@ -149,20 +141,105 @@ def student_list():
    <p><a href="{url_for('index')}">← Về trang chủ</a></p>
    """

# Trang chi tiết sinh viên (để tạo đường dẫn MSSV)

# ---------------- CÂU 3: CHI TIẾT SINH VIÊN ( /students/<mssv> ) ----------------
@app.route("/students/<mssv>")
def student_detail(mssv):
    if mssv not in STUDENTS:
        abort(404, description=f"Không có sinh viên với MSSV = {mssv}.")

    student = STUDENTS.get(mssv)
    if not student:
        return "Không tìm thấy sinh viên!", 404
    return f"Trang chi tiết của sinh viên: <b>{escape(student['name'])}</b> ({mssv})"
    dtb, xep_loai = tinh_diem_va_xep_loai(student["scores"])

    lop_link = url_for("student_list", lop=student["lop"])
    export_link = url_for("export_student_csv", mssv=mssv)  # Link tải CSV (Câu 5)
    short_link = url_for("short_student_detail", mssv=mssv)  # Link rút gọn (Câu 4)

    scores_dict = student["scores"]

    if not scores_dict:
        scores_table = "<p><i>Chưa có điểm học phần nào.</i></p>"
    else:
        scores_rows = ""
        for mon, diem in scores_dict.items():
            scores_rows += f"""
            <tr>
                <td>{escape(mon)}</td>
                <td>{diem}</td>
            </tr>
            """
        scores_table = f"""
        <table border="1" cellpadding="6" cellspacing="0">
            <thead>
                <tr>
                    <th>Môn học</th>
                    <th>Điểm</th>
                </tr>
            </thead>
            <tbody>
                {scores_rows}
            </tbody>
        </table>
        """

    return f"""
    <h1>Chi tiết sinh viên</h1>
    <hr>
    <ul>
        <li><b>MSSV:</b> {mssv}</li>
        <li><b>Họ tên:</b> {escape(student['name'])}</li>
        <li><b>Lớp:</b> <a href="{lop_link}">{escape(student['lop'])}</a></li>
        <li><b>Điểm TB:</b> {dtb}</li>
        <li><b>Xếp loại:</b> {xep_loai}</li>
        <li><b>Link rút gọn (Câu 4):</b> <a href="{short_link}">{request.host_url[:-1]}{short_link}</a></li>
    </ul>

    <h3>Bảng điểm từng học phần:</h3>
    {scores_table}
    
    <br>
    <!-- Link tải CSV theo yêu cầu Câu 5 -->
    <p>📥 <a href="{export_link}"><b>Tải bảng điểm (CSV)</b></a></p>
    <br>
    <p><a href="{url_for('student_list')}">← Quay lại danh sách sinh viên</a></p>
    """


# ---------------- CÂU 4: LINK RÚT GỌN ( /sv/<mssv> ) ----------------
@app.route("/sv/<mssv>")
def short_student_detail(mssv):
    return redirect(url_for("student_detail", mssv=mssv), code=301)


# ---------------- CÂU 5: XUẤT BẢNG ĐIỂM CSV ( /students/<mssv>/export ) ----------------
@app.route("/students/<mssv>/export")
def export_student_csv(mssv):
    # 1. Kiểm tra MSSV nếu không tồn tại -> 404
    if mssv not in STUDENTS:
        abort(404, description=f"Không có sinh viên với MSSV = {mssv}.")

    student = STUDENTS[mssv]
    scores = student["scores"]

    # 2. Xây dựng nội dung file CSV
    csv_lines = ["hoc_phan,diem"]
    for mon, diem in scores.items():
        csv_lines.append(f"{mon},{diem}")
    
    csv_content = "\n".join(csv_lines)

    # 3. Tạo HTTP Response để trình duyệt tự động tải xuống
    response = make_response(csv_content)
    response.headers["Content-Type"] = "text/csv; charset=utf-8"
    response.headers["Content-Disposition"] = f"attachment; filename=diem_{mssv}.csv"

    return response


# API sinh viên theo yêu cầu đề bài Câu 1
@app.route("/api/students")
def api_students():
    return STUDENTS

if __name__ == "__main__":
    app.run(debug=True, port=8000)


if __name__ == "__main__":
    app.run(debug=True, port=8000)
