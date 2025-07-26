from sqlalchemy import create_engine
import streamlit as st
import pandas as pd

# เชื่อมต่อฐานข้อมูล
engine = create_engine("mysql+pymysql://root:651324@localhost:3306/review_dashboard")
connection = engine.connect()
print("เชื่อมต่อฐานข้อมูลสำเร็จ!")


# Query ข้อมูลตัวอย่าง
query = "SELECT * FROM reviews;"  # สมมติว่าคุณมีตาราง reviews
df = pd.read_sql(query, connection)

# แสดงผลบนหน้าเว็บด้วย Streamlit
st.title("Dashboard รีวิวสินค้า")
st.dataframe(df)



# วิธีเรียกใช้งาน fujikathailand

from scraping.fujikathailand import fetch_fujika_posts

posts = fetch_fujika_posts(status="private", limit=5)

for post in posts:
    print(post["title"], post["link"])
