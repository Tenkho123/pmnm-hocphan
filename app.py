import os
import sqlite3
from datetime import timedelta
from math import sqrt
from flask import (
    Flask, render_template, request, redirect, 
    url_for, jsonify, flash, session, abort
)
from markupsafe import escape
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError

base_dir = os.path.abspath(os.path.dirname(__file__))
template_dir = os.path.join(base_dir, 'templates')
static_dir = os.path.join(base_dir, 'static')

app = Flask(__name__)
app.secret_key = "pmnm_husc_secret_key_2026"
app.permanent_session_lifetime = timedelta(days=7)
app.json.ensure_ascii = False

# ==============================================================================
# CẤU HÌNH DATABASE SQLITE (Tương thích Vercel Serverless /tmp)
# ==============================================================================
# Trên Vercel, chỉ thư mục /tmp là có quyền ghi (writeable)
if os.environ.get("VERCEL"):
    DB_FILE = "/tmp/demo.db"
else:
    os.makedirs(app.instance_path, exist_ok=True)
    DB_FILE = os.path.join(app.instance_path, "demo.db")

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS students (
                mssv TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                gpa REAL NOT NULL
            )
        ''')
        cursor.execute("SELECT COUNT(*) FROM students")
        row = cursor.fetchone()
        if row and row[0] == 0:
            sample_students = [
                ("23T1020200", "Nguyễn Văn An", 8.5),
                ("23T1020205", "Lê Hoàng Nam", 7.8),
                ("23T1020210", "Trần Thị Mai", 9.2),
                ("23T1020215", "Phạm Minh Đức", 6.5),
                ("23T1020220", "Vũ Thùy Linh", 8.9),
                ("23T1020225", "Đặng Bảo Lâm", 7.2)
            ]
            cursor.executemany(
                "INSERT INTO students (mssv, name, gpa) VALUES (?, ?, ?)", 
                sample_students
            )
        conn.commit()

# Khởi tạo DB
init_db()

# ==============================================================================
# DỮ LIỆU MẪU IN-MEMORY (Sổ điểm & Auth)
# ==============================================================================
STUDENTS_DICT = {
    "23T1020001": {"name": "Nguyễn Văn An", "lop": "K47A", "scores": {"PMMNM": 8.5, "CSDL": 7.0, "MMT": 9.0}},
    "23T1020002": {"name": "Trần Thị Bình", "lop": "K47A", "scores": {"PMMNM": 6.0, "CSDL": 5.5, "MMT": 7.0}},
    "23T1020003": {"name": "Lê Hoàng Cường", "lop": "K47B", "scores": {"PMMNM": 9.5, "CSDL": 9.0}},
    "23T1020004": {"name": "Phạm Văn Dũng", "lop": "K47B", "scores": {"PMMNM": 4.0, "CSDL": 3.5, "MMT": 5.0}},
    "23T1020005": {"name": "Hoàng Thu Hà", "lop": "K47A", "scores": {}},
    "23T1020006": {"name": "Võ Quốc Khánh", "lop": "K47C", "scores": {"PMMNM": 7.5, "MMT": 8.0}},
}

USERS = [
    {"username": "admin", "password": "123", "email": "admin@husc.edu.vn"}
]

# ==============================================================================
# JINJA2 FILTERS & CONTEXT PROCESSOR
# ==============================================================================
@app.template_filter("vnd")
def format_vnd(value):
    try:
        return f"{float(value):,.0f} ₫".replace(",", ".")
    except (ValueError, TypeError):
        return value

@app.context_processor
def inject_global_data():
    return {
        "site_title": "PMNM Portal - HUSC",
        "current_year": 2026,
        "author_name": "Sinh viên Khoa CNTT - ĐH Khoa học Huế"
    }

# ==============================================================================
# ROUTE 1: TRANG CHỦ TỔNG HỢP (PORTAL DASHBOARD)
# ==============================================================================
@app.route("/")
def index():
    return render_template("index.html")

# ==============================================================================
# CHƯƠNG 3: SỔ ĐIỂM SINH VIÊN (Routing, Query Params, Chi tiết)
# ==============================================================================
def tinh_diem_tb(scores):
    if not scores:
        return None, "Chưa có điểm"
    dtb = sum(scores.values()) / len(scores)
    if dtb >= 8.5:
        xl = "Giỏi"
    elif dtb >= 7.0:
        xl = "Khá"
    elif dtb >= 5.0:
        xl = "Trung bình"
    else:
        xl = "Yếu"
    return round(dtb, 2), xl

@app.route("/sodiem")
def sodiem_list():
    selected_lop = request.args.get("lop", "").strip()
    ds_lop = sorted(list(set(st["lop"] for st in STUDENTS_DICT.values())))
    
    filtered_students = {}
    for mssv, data in STUDENTS_DICT.items():
        if not selected_lop or data["lop"].lower() == selected_lop.lower():
            dtb, xl = tinh_diem_tb(data["scores"])
            filtered_students[mssv] = {**data, "dtb": dtb, "xep_loai": xl}
            
    return render_template(
        "sodiem.html", 
        students=filtered_students, 
        ds_lop=ds_lop, 
        selected_lop=selected_lop
    )

@app.route("/sodiem/<mssv>")
def sodiem_detail(mssv):
    student = STUDENTS_DICT.get(mssv)
    if not student:
        abort(404, description=f"Không tìm thấy sinh viên có mã {mssv}")
    dtb, xl = tinh_diem_tb(student["scores"])
    return render_template("sodiem_detail.html", mssv=mssv, student=student, dtb=dtb, xl=xl)

@app.route("/api/sodiem")
def api_sodiem():
    return jsonify(STUDENTS_DICT)

# ==============================================================================
# CHƯƠNG 4: BỘ CÔNG CỤ TÍNH TOÁN (Math, Score, BMI)
# ==============================================================================
@app.route("/calculator", methods=["GET", "POST"])
def calculator():
    result, error = None, None
    if request.method == "POST":
        try:
            a_val = float(request.form.get("a", "").replace(",", "."))
            b_val = float(request.form.get("b", "").replace(",", "."))
            op = request.form.get("op")
            if op == "+": result = a_val + b_val
            elif op == "-": result = a_val - b_val
            elif op == "*": result = a_val * b_val
            elif op == "/":
                if b_val == 0: error = "Không thể chia cho 0!"
                else: result = a_val / b_val
            else: error = "Phép toán không hợp lệ!"
        except (ValueError, TypeError):
            error = "Vui lòng nhập số hợp lệ!"
    return render_template("calculator.html", result=result, error=error)

@app.route("/score", methods=["GET", "POST"])
def score_calculator():
    result, error = None, None
    if request.method == "POST":
        try:
            cc = float(request.form.get("a", "").replace(",", "."))
            gk = float(request.form.get("b", "").replace(",", "."))
            ck = float(request.form.get("c", "").replace(",", "."))
            
            if not (0 <= cc <= 10 and 0 <= gk <= 10 and 0 <= ck <= 10):
                error = "Điểm các cột phải trong khoảng từ 0 đến 10!"
            else:
                final_score = round(cc * 0.1 + gk * 0.3 + ck * 0.6, 2)
                if cc < 1 or gk < 1 or ck < 1:
                    grade = "F (Liệt điểm thành phần < 1.0)"
                elif final_score >= 8.5: grade = "A"
                elif final_score >= 7.0: grade = "B"
                elif final_score >= 5.5: grade = "C"
                elif final_score >= 4.0: grade = "D"
                else: grade = "F"
                result = f"{final_score} (Hệ chữ: {grade})"
        except (ValueError, TypeError):
            error = "Vui lòng nhập điểm số đầy đủ và chính xác!"
    return render_template("score.html", result=result, error=error)

@app.route("/bmi", methods=["GET", "POST"])
def bmi_calculator():
    result, error, color = None, None, ""
    if request.method == "POST":
        try:
            height = float(request.form.get("a", "").replace(",", "."))
            weight = float(request.form.get("b", "").replace(",", "."))
            if not (50 <= height <= 250):
                error = "Chiều cao không hợp lệ (nhập từ 50 - 250 cm)"
            elif not (10 <= weight <= 300):
                error = "Cân nặng không hợp lệ (nhập từ 10 - 300 kg)"
            else:
                bmi = round(weight / ((height / 100) ** 2), 2)
                if bmi < 18.5:
                    status, color = "Thiếu cân", "warning"
                elif bmi < 23:
                    status, color = "Bình thường", "success"
                elif bmi < 25:
                    status, color = "Thừa cân", "primary"
                else:
                    status, color = "Béo phì", "danger"
                result = f"BMI = {bmi} ({status})"
        except (ValueError, TypeError):
            error = "Vui lòng nhập giá trị hợp lệ!"
    return render_template("bmi.html", result=result, error=error, color=color)

# ==============================================================================
# CHƯƠNG 6: QUẢN LÝ SINH VIÊN VỚI SQLITE (CRUD, Filter, Statistics)
# ==============================================================================
@app.route("/students-sql", methods=["GET"])
def students_sql():
    init_db()  # Đảm bảo bảng luôn tồn tại nếu Vercel tạo container mới
    search_query = request.args.get("search", "").strip()
    min_gpa = request.args.get("min_gpa", "").strip()
    sort_option = request.args.get("sort", "name_asc")

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*), AVG(gpa), MAX(gpa), MIN(gpa) FROM students")
        stats_row = cursor.fetchone()
        stats = {
            "total": stats_row[0] or 0,
            "avg": round(stats_row[1], 2) if stats_row[1] is not None else 0.0,
            "max": stats_row[2] or 0.0,
            "min": stats_row[3] or 0.0
        }

        sql = "SELECT * FROM students WHERE 1=1"
        params = []
        if search_query:
            sql += " AND (name LIKE ? OR mssv LIKE ?)"
            params.extend([f"%{search_query}%", f"%{search_query}%"])
        if min_gpa:
            try:
                sql += " AND gpa >= ?"
                params.append(float(min_gpa))
            except ValueError:
                pass

        if sort_option == "gpa_desc": sql += " ORDER BY gpa DESC"
        elif sort_option == "gpa_asc": sql += " ORDER BY gpa ASC"
        elif sort_option == "name_desc": sql += " ORDER BY name DESC"
        else: sql += " ORDER BY name ASC"

        cursor.execute(sql, params)
        students = [dict(row) for row in cursor.fetchall()]

    return render_template(
        "students_sql.html",
        students=students,
        stats=stats,
        search_query=search_query,
        min_gpa=min_gpa,
        sort_option=sort_option
    )

@app.route("/students-sql/add", methods=["POST"])
def add_student_sql():
    mssv = request.form.get("mssv", "").strip()
    name = request.form.get("name", "").strip()
    gpa = request.form.get("gpa", "").strip()
    if mssv and name and gpa:
        try:
            with get_db_connection() as conn:
                conn.cursor().execute(
                    "INSERT INTO students (mssv, name, gpa) VALUES (?, ?, ?)",
                    (mssv, name, float(gpa))
                )
                conn.commit()
            flash("Thêm sinh viên thành công!", "success")
        except sqlite3.IntegrityError:
            flash("Lỗi: Mã sinh viên (MSSV) này đã tồn tại!", "danger")
    return redirect(url_for("students_sql"))

@app.route("/students-sql/quick-bonus", methods=["POST"])
def quick_bonus():
    mssv = request.form.get("mssv")
    with get_db_connection() as conn:
        conn.cursor().execute(
            "UPDATE students SET gpa = MIN(10.0, ROUND(gpa + 0.5, 2)) WHERE mssv = ?",
            (mssv,)
        )
        conn.commit()
    flash("Đã cộng 0.5 điểm GPA!", "info")
    return redirect(url_for("students_sql"))

@app.route("/students-sql/delete", methods=["POST"])
def delete_student_sql():
    mssv = request.form.get("mssv")
    with get_db_connection() as conn:
        conn.cursor().execute("DELETE FROM students WHERE mssv = ?", (mssv,))
        conn.commit()
    flash("Đã xóa sinh viên!", "warning")
    return redirect(url_for("students_sql"))

# ==============================================================================
# HỆ THỐNG AUTH: FLASK-WTF (Register, Login, Session)
# ==============================================================================
class RegisterForm(FlaskForm):
    username = StringField("Tên tài khoản", validators=[DataRequired(), Length(min=4, max=20)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Mật khẩu", validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField("Xác nhận mật khẩu", validators=[DataRequired(), EqualTo("password", message="Mật khẩu không khớp")])
    accept_terms = BooleanField("Tôi đồng ý với các điều khoản", validators=[DataRequired(message="Cần tích chọn đồng ý")])
    submit = SubmitField("Đăng ký tài khoản")

    def validate_username(self, username):
        for user in USERS:
            if user["username"].lower() == username.data.lower():
                raise ValidationError("Tên tài khoản đã tồn tại!")

@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        USERS.append({
            "username": form.username.data,
            "email": form.email.data,
            "password": form.password.data
        })
        flash("Đăng ký thành công! Hãy đăng nhập.", "success")
        return redirect(url_for("login"))
    return render_template("register.html", form=form)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        u = request.form.get("username")
        p = request.form.get("password")
        remember = request.form.get("remember")
        user = next((x for x in USERS if x["username"] == u and x["password"] == p), None)
        if user:
            session["username"] = user["username"]
            session.permanent = bool(remember)
            flash("Đăng nhập thành công!", "success")
            return redirect(url_for("profile"))
        flash("Sai tên tài khoản hoặc mật khẩu!", "danger")
    return render_template("login.html")

@app.route("/profile")
def profile():
    if "username" not in session:
        flash("Vui lòng đăng nhập để xem hồ sơ!", "warning")
        return redirect(url_for("login"))
    return render_template("profile.html", username=session["username"])

@app.route("/logout")
def logout():
    session.pop("username", None)
    flash("Bạn đã đăng xuất.", "info")
    return redirect(url_for("login"))

# ==============================================================================
# BÁO CÁO BÀI TẬP LÝ THUYẾT (Bài 1.1, 1.2, 2.1, 2.3 từ Slide PDF)
# ==============================================================================
@app.route("/docs")
def docs():
    return render_template("docs.html")

@app.errorhandler(404)
def page_not_found(e):
    return render_template("base.html", not_found=True, error_msg=escape(str(e))), 404

if __name__ == "__main__":
    app.run(debug=True, port=8000)