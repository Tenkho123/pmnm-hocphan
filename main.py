import importlib.util
from pathlib import Path

# Trỏ trực tiếp tới file bài tập của bạn
target_file = Path(__file__).resolve().parent / "baitap" / "chuong3-sodiem.py"

spec = importlib.util.spec_from_file_location("chuong3_sodiem", target_file)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

# Cung cấp app Flask cho Vercel
app = module.app
