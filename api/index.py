import importlib.util
from pathlib import Path

# Lấy đường dẫn tới file bài tập chuong3-sodiem.py
base_dir = Path(__file__).resolve().parent.parent
target_file = base_dir / "baitap" / "chuong3-sodiem.py"

# Nạp code động (để tránh lỗi cú pháp do dấu gạch ngang '-')
spec = importlib.util.spec_from_file_location("chuong3_sodiem", target_file)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

# Cung cấp biến app cho Vercel
app = module.app
