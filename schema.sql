DROP TABLE IF EXISTS books;
DROP TABLE IF EXISTS categories;

CREATE TABLE categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT
);

CREATE TABLE books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    year INTEGER,
    price REAL,
    category_id INTEGER NOT NULL,
    FOREIGN KEY (category_id) REFERENCES categories (id) ON DELETE CASCADE
);

-- Thêm vài dữ liệu mẫu ban đầu để giao diện có cái hiển thị ngay
INSERT INTO categories (name, description) VALUES 
('Công nghệ thông tin', 'Sách về lập trình, giải thuật, cơ sở dữ liệu'),
('Kinh tế', 'Sách tài chính, quản trị kinh doanh'),
('Văn học', 'Tiểu thuyết, truyện ngắn');

INSERT INTO books (title, author, year, price, category_id) VALUES 
('Lập trình Python cơ bản', 'Nguyễn Dũng', 2023, 120000, 1),
('Tìm hiểu Flask Web', 'Trần Văn A', 2024, 95000, 1),
('Kinh tế vi mô', 'Lê Thị B', 2022, 85000, 2),
('Dế Mèn phiêu lưu ký', 'Tô Hoài', 2020, 50000, 3);