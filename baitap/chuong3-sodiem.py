from flask import Flask, abort, request, url_for, make_response, redirect
from markupsafe import escape

app = Flask(__name__)

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


# ---------------- CÂU 1: TRANG CHỦ ( / ) ----------------
@app.route("/")
def index():
    total_students = len(STUDENTS)
    ds_lop = set(st["lop"] for st in STUDENTS.values())
    total_classes = len(ds_lop)

    students_link = url_for("student_list")
    classes_link = url_for("api_students")
    search_link = url_for("search")

    return f"""
    <h1>Trang chủ Quản lý Sinh viên</h1>
    <hr>
    <h3>Thống kê tổng quan:</h3>
    <ul>
        <li><b>Tổng số sinh viên:</b> {total_students} sinh viên</li>
        <li><b>Tổng số lớp:</b> {total_classes} lớp ({", ".join(sorted(ds_lop))})</li>
    </ul>
    
    <h3>Liên kết điều hướng:</h3>
    <ul>
        <li><a href="{students_link}">Xem danh sách sinh viên</a></li>
        <li><a href="{search_link}">Tìm kiếm sinh viên</a></li>
        <li><a href="{classes_link}">API Sinh viên (/api/students)</a></li>
    </ul>
    """


# ---------------- CÂU 2: BẢNG DANH SÁCH ( /students ) ----------------
@app.route("/students")
def student_list():
    selected_lop = request.args.get("lop", "").strip()
    danh_sach_lop = sorted(list(set(st["lop"] for st in STUDENTS.values())))
    
    filter_html = f'<a href="{url_for("student_list")}">Tất cả</a>'
    for c in danh_sach_lop:
        filter_html += f' | <a href="{url_for("student_list", lop=c)}">{c}</a>'
        
    rows_html = ""
    match_count = 0
    
    for mssv, info in STUDENTS.items():
        if selected_lop and info["lop"].lower() != selected_lop.lower():
            continue
            
        match_count += 1
        dtb, xep_loai = tinh_diem_va_xep_loai(info["scores"])
        detail_url = url_for("student_detail", mssv=mssv)
        
        rows_html += f"""
        <tr>
            <td><a href="{detail_url}">{mssv}</a></td>
            <td>{escape(info['name'])}</td>
            <td>{escape(info['lop'])}</td>
            <td>{dtb}</td>
            <td>{xep_loai}</td>
        </tr>
        """
        
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


# ---------------- CÂU 3: CHI TIẾT SINH VIÊN ( /students/<mssv> ) ----------------
@app.route("/students/<mssv>")
def student_detail(mssv):
    if mssv not in STUDENTS:
        abort(404, description=f"Không có sinh viên với MSSV = {mssv}.")

    student = STUDENTS.get(mssv)
    dtb, xep_loai = tinh_diem_va_xep_loai(student["scores"])

    lop_link = url_for("student_list", lop=student["lop"])
    export_link = url_for("export_student_csv", mssv=mssv)
    short_link = url_for("short_student_detail", mssv=mssv)

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
    if mssv not in STUDENTS:
        abort(404, description=f"Không có sinh viên với MSSV = {mssv}.")

    student = STUDENTS[mssv]
    scores = student["scores"]

    csv_lines = ["hoc_phan,diem"]
    for mon, diem in scores.items():
        csv_lines.append(f"{mon},{diem}")
    
    csv_content = "\n".join(csv_lines)

    response = make_response(csv_content)
    response.headers["Content-Type"] = "text/csv; charset=utf-8"
    response.headers["Content-Disposition"] = f"attachment; filename=diem_{mssv}.csv"

    return response


# ---------------- CÂU 6: TÌM KIẾM AN TOÀN ( /search?q=... ) ----------------
@app.route("/search")
def search():
    # 1. Đọc từ khóa 'q' từ Query String
    q = request.args.get("q", "").strip()
    
    results = []
    if q:
        q_lower = q.lower()
        # Tìm sinh viên có Họ tên HOẶC MSSV chứa từ khóa (không phân biệt hoa thường)
        for mssv, info in STUDENTS.items():
            if q_lower in info["name"].lower() or q_lower in mssv.lower():
                results.append((mssv, info))

    # 2. Tạo nội dung danh sách kết quả
    if q:
        # CHÚ Ý XSS: Dùng escape(q) ở thông báo số lượng
        result_title = f"<p>Tìm thấy <b>{len(results)}</b> kết quả cho \"<b>{escape(q)}</b>\"</p>"
        if not results:
            results_content = "<p>Không tìm thấy sinh viên phù hợp.</p>"
        else:
            items_html = ""
            for mssv, info in results:
                detail_url = url_for("student_detail", mssv=mssv)
                items_html += f"<li><a href='{detail_url}'>{mssv} - {escape(info['name'])}</a> ({escape(info['lop'])})</li>"
            results_content = f"<ul>{items_html}</ul>"
    else:
        result_title = ""
        results_content = ""

    # 3. CHÚ Ý XSS: Dùng escape(q) trong thuộc tính value="..." của thẻ <input>
    return f"""
    <h1>Tìm kiếm sinh viên</h1>
    <hr>
    <form action="{url_for('search')}" method="GET">
        <input type="text" name="q" value="{escape(q)}" placeholder="Nhập tên hoặc MSSV..." size="30" />
        <button type="submit">Tìm kiếm</button>
    </form>

    {result_title}
    {results_content}

    <br>
    <p><a href="{url_for('index')}">← Về trang chủ</a></p>
    """


@app.route("/api/students")
def api_students():
    return STUDENTS


if __name__ == "__main__":
    app.run(debug=True, port=8000)
