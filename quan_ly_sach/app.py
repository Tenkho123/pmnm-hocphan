import sqlite3
from flask import Flask, render_template, request, redirect, url_for, abort

app = Flask(__name__)
# Cho phép JSON hiển thị tiếng Việt có dấu đúng chuẩn học phần
app.json.ensure_ascii = False 

DATABASE = 'library.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # Cho phép gọi row['col_name']
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

# Filter format tiền VND tự viết theo bài giảng chương 4
@app.template_filter('vnd')
def format_vnd(value):
    if value is None:
        return "0 ₫"
    return f"{int(value):,} ₫".replace(',', '.')

# --- 1. DASHBOARD ---
@app.route("/")
def dashboard():
    conn = get_db()
    total_books = conn.execute("SELECT COUNT(*) FROM books").fetchone()[0]
    total_categories = conn.execute("SELECT COUNT(*) FROM categories").fetchone()[0]
    
    # Lấy 5 sách vừa thêm mới nhất
    recent_books = conn.execute("""
        SELECT b.*, c.name as category_name 
        FROM books b 
        JOIN categories c ON b.category_id = c.id 
        ORDER BY b.id DESC LIMIT 5
    """).fetchall()

    # Thống kê số sách theo từng danh mục
    category_stats = conn.execute("""
        SELECT c.id, c.name, COUNT(b.id) as book_count 
        FROM categories c 
        LEFT JOIN books b ON c.id = b.category_id 
        GROUP BY c.id, c.name
    """).fetchall()

    conn.close()
    return render_template(
        "dashboard.html",
        total_books=total_books,
        total_categories=total_categories,
        recent_books=recent_books,
        category_stats=category_stats
    )

# --- 2. QUẢN LÝ DANH MỤC (CRUD Categories) ---
@app.route("/categories", methods=["GET", "POST"])
def categories():
    conn = get_db()
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip()
        if name:
            conn.execute("INSERT INTO categories (name, description) VALUES (?, ?)", (name, description))
            conn.commit()
            conn.close()
            return redirect(url_for("categories"))

    categories_list = conn.execute("""
        SELECT c.*, COUNT(b.id) as book_count 
        FROM categories c 
        LEFT JOIN books b ON c.id = b.category_id 
        GROUP BY c.id
    """).fetchall()
    conn.close()
    return render_template("categories.html", categories=categories_list)

@app.route("/categories/edit/<int:cat_id>", methods=["GET", "POST"])
def edit_category(cat_id):
    conn = get_db()
    cat = conn.execute("SELECT * FROM categories WHERE id = ?", (cat_id,)).fetchone()
    if cat is None:
        abort(404)

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip()
        if name:
            conn.execute("UPDATE categories SET name = ?, description = ? WHERE id = ?", (name, description, cat_id))
            conn.commit()
            conn.close()
            return redirect(url_for("categories"))

    conn.close()
    return render_template("edit_category.html", category=cat)

@app.route("/categories/delete/<int:cat_id>", methods=["POST"])
def delete_category(cat_id):
    conn = get_db()
    conn.execute("DELETE FROM categories WHERE id = ?", (cat_id,))
    conn.commit()
    conn.close()
    return redirect(url_for("categories"))

# --- 3. QUẢN LÝ SÁCH (CRUD Books + Lọc theo danh mục) ---
@app.route("/books", methods=["GET", "POST"])
def books():
    conn = get_db()
    
    # Xử lý thêm sách mới
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        author = request.form.get("author", "").strip()
        year = request.form.get("year", type=int)
        price = request.form.get("price", type=float)
        category_id = request.form.get("category_id", type=int)

        if title and category_id:
            conn.execute("""
                INSERT INTO books (title, author, year, price, category_id) 
                VALUES (?, ?, ?, ?, ?)
            """, (title, author, year, price, category_id))
            conn.commit()
            conn.close()
            return redirect(url_for("books"))

    # Lọc sách theo danh mục nếu người dùng truyền ?category_id=...
    selected_cat = request.args.get("category_id", type=int)
    
    if selected_cat:
        book_list = conn.execute("""
            SELECT b.*, c.name as category_name 
            FROM books b 
            JOIN categories c ON b.category_id = c.id 
            WHERE b.category_id = ? 
            ORDER BY b.id DESC
        """, (selected_cat,)).fetchall()
    else:
        book_list = conn.execute("""
            SELECT b.*, c.name as category_name 
            FROM books b 
            JOIN categories c ON b.category_id = c.id 
            ORDER BY b.id DESC
        """).fetchall()

    categories_list = conn.execute("SELECT * FROM categories").fetchall()
    conn.close()

    return render_template(
        "books.html",
        books=book_list,
        categories=categories_list,
        selected_cat=selected_cat
    )

@app.route("/books/edit/<int:book_id>", methods=["GET", "POST"])
def edit_book(book_id):
    conn = get_db()
    book = conn.execute("SELECT * FROM books WHERE id = ?", (book_id,)).fetchone()
    if book is None:
        abort(404)

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        author = request.form.get("author", "").strip()
        year = request.form.get("year", type=int)
        price = request.form.get("price", type=float)
        category_id = request.form.get("category_id", type=int)

        if title and category_id:
            conn.execute("""
                UPDATE books 
                SET title = ?, author = ?, year = ?, price = ?, category_id = ? 
                WHERE id = ?
            """, (title, author, year, price, category_id, book_id))
            conn.commit()
            conn.close()
            return redirect(url_for("books"))

    categories_list = conn.execute("SELECT * FROM categories").fetchall()
    conn.close()
    return render_template("edit_book.html", book=book, categories=categories_list)

@app.route("/books/delete/<int:book_id>", methods=["POST"])
def delete_book(book_id):
    conn = get_db()
    conn.execute("DELETE FROM books WHERE id = ?", (book_id,))
    conn.commit()
    conn.close()
    return redirect(url_for("books"))

# --- Xử lý 404 tùy biến ---
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

if __name__ == "__main__":
    app.run(debug=True, port=8000)