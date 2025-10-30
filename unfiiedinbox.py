from database.all_database import get_connection

try:
    conn = get_connection()
    print("✅ เชื่อมต่อฐานข้อมูลสำเร็จ!")
    conn.close()
except Exception as e:
    print("❌ เกิดข้อผิดพลาด:", e)