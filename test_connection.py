# test_connection.py

from database.db_utils import engine
import pandas as pd

# ลองสั่งดูตารางในฐานข้อมูล
try:
    df = pd.read_sql("SHOW TABLES", engine)
    print("เชื่อมต่อสำเร็จ ✅")
    print(df)
except Exception as e:
    print("เกิดข้อผิดพลาด ❌")
    print(e)
