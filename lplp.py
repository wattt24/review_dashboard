# import pandas as pd

# # สร้างข้อมูลเป็น list ของ dictionary
# data = [
#     {"text": "ชอบสินค้ามากเลยค่ะ", "label": "คำชม"},
#     {"text": "ทำไมส่งของช้าจัง", "label": "คำร้องเรียน"},
#     {"text": "มีสีอื่นไหมคะ", "label": "คำถาม"},
#     {"text": "มีไซส์อื่นไหมคะ", "label": "คำถาม"},
# ]

# # แปลงเป็น DataFrame
# df = pd.DataFrame(data)

# # บันทึกเป็นไฟล์ CSV
# df.to_csv("thai_feedback_dataset.csv", index=False, encoding="utf-8-sig")

# print("✅ สร้างไฟล์ thai_feedback_dataset.csv สำเร็จ!")
# lplp.py
# lplp.py
import streamlit as st
import pandas as pd
import plotly.express as px
from database.all_database import get_reviews_by_period, get_all_reviews

from datetime import datetime

st.set_page_config(page_title="Fujikathailand Reviews", layout="wide")

st.title("📊 Dashboard รีวิว Fujikathailand.com")

# ---- เลือกช่วงเวลา ----
period_option = st.selectbox(
    "เลือกช่วงเวลาของรีวิว:",
    ["ทั้งหมด", "1 เดือน", "3 เดือน", "1 ปี"],
    index=0
)

# แปลงเป็นจำนวนเดือน
period_mapping = {
    "ทั้งหมด": None,
    "1 เดือน": 1,
    "3 เดือน": 3,
    "1 ปี": 12
}
months = period_mapping[period_option]


# ---- ดึงข้อมูลรีวิวตามช่วงเวลา ----
@st.cache_data
def get_fujikathailand_reviews_by_period(months=None):
    if months is None:
        # ดึงทั้งหมด
        df = get_all_reviews(platform="fujikathailand")
    else:
        # ดึงตามจำนวนเดือน
        df = get_reviews_by_period(platform="fujikathailand", months=months)
    return df


df = get_fujikathailand_reviews_by_period(months=months)

if df.empty:
    st.warning("❌ ไม่มีข้อมูลรีวิว")
else:
    # ---- กราฟ Rating ----
    st.subheader("📊 การกระจาย Rating")
    rating_counts = df['rating'].value_counts().sort_index()
    fig = px.bar(
        x=rating_counts.index.astype(str),
        y=rating_counts.values,
        labels={'x': 'Rating', 'y': 'จำนวนรีวิว'},
        text=rating_counts.values,
        color=rating_counts.index.astype(str),
        color_discrete_sequence=px.colors.qualitative.Bold
    )
    fig.update_traces(textposition='outside')
    fig.update_layout(
        xaxis=dict(title='Rating'),
        yaxis=dict(title='จำนวนรีวิว'),
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    st.plotly_chart(fig, use_container_width=True)

    # ---- สรุปค่าเฉลี่ย Rating และจำนวนรีวิว ----
    # ---- ตารางรีวิวแบบ interactive ----
    display_df = df.copy()
    display_df['review_date'] = pd.to_datetime(display_df['review_date'])
    display_df = display_df.sort_values(by='review_date', ascending=False)

    # สร้างคอลัมน์ 'ลำดับ' จาก index
    display_df.reset_index(drop=True, inplace=True)
    display_df['ลำดับ'] = display_df.index + 1

    # เปลี่ยนชื่อคอลัมน์เป็นภาษาไทย
    display_df.rename(columns={
        'platform': 'แพลตฟอร์ม',
        'shop_id': 'รหัสร้านค้า',
        'product_id': 'รหัสสินค้า',
        'review_id': 'รหัสรีวิว',
        'rating': 'คะแนน',
        'sentiment': 'อารมณ์รีวิว',
        'review_text': 'ข้อความรีวิว',
        'keywords': 'คำสำคัญ',
        'review_date': 'วันที่รีวิว'
    }, inplace=True)

    # ใช้ toggle เปิด/ปิดตาราง
    show_table_02 = st.toggle("👀 ดูตารางรีวิว", value=False)
    if show_table_02:
        st.dataframe(
            display_df[["ลำดับ", "แพลตฟอร์ม", "รหัสร้านค้า", "ข้อความรีวิว", "อารมณ์รีวิว", "วันที่รีวิว"]],
            use_container_width=True,
            height=550
        )

    # ---- ดาวน์โหลด CSV ----
    csv_data_export = display_df.to_csv(index=False, encoding='utf-8-sig')
    st.download_button(
        label="📥 ดาวน์โหลด",
        data=csv_data_export,
        file_name=f"fujikathailand_reviews_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )

    # ---- กราฟเส้น Rating เฉลี่ยรายวันหลาย Platform ----


