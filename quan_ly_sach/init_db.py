import sqlite3

connection = sqlite3.connect('library.db')

with open('schema.sql', encoding='utf-8') as f:
    connection.executescript(f.read())

connection.commit()
connection.close()
print("-> Đã khởi tạo cơ sở dữ liệu library.db thành công!")