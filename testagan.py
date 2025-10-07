from database.all_database import get_all_reviews, get_reviews_by_period
import pandas as pd
import streamlit as st
import plotly.express as px
from datetime import datetime

# 🧭 ตั้งค่าหน้าเว็บ
st.set_page_config(
    page_title="Review Insight Dashboard",
    page_icon="📊",
    layout="wide"
)

# 🎨 CSS ตกแต่งเบาๆ ให้เหมือนเว็บจริง
st.markdown("""
<style>
    .main {
        background-color: #f8f9fa;
        font-family: 'Segoe UI', sans-serif;
    }
    h1, h2, h3 {
        color: #1e3a8a;
    }
    .stMetric {
        background-color: #ffffff;
        border-radius: 12px;
        box-shadow: 0px 1px 3px rgba(0,0,0,0.1);
        padding: 10px;
    }
</style>
""", unsafe_allow_html=True)

# 🏷️ ส่วนหัว
st.title("📊 Review Insight Dashboard")
st.markdown("ระบบวิเคราะห์รีวิวจากหลายแพลตฟอร์ม เพื่อดูแนวโน้มความคิดเห็นและความพึงพอใจของลูกค้า")
st.divider()

# 🔽 ส่วนกรองข้อมูล
with st.container():
    col1, col2, col3 = st.columns([1,1,1])

    with col1:
        period_option = st.selectbox(
            "🕒 เลือกช่วงเวลา",
            ("ทั้งหมด", "1 เดือน", "3 เดือน", "1 ปี")
        )

    with col2:
        platform_option = st.selectbox(
            "🌐 แพลตฟอร์ม",
            ("ทั้งหมด", "fujikathailand", "FACEBOOK", "SHOPEE", "LAZADA" , "LINE")
        )

    with col3:
        show_chart = st.toggle("📈 แสดงกราฟสรุป", value=True)

# แปลงค่าช่วงเวลาเป็นเดือน
months = None
if period_option == "1 เดือน":
    months = 1
elif period_option == "3 เดือน":
    months = 3
elif period_option == "1 ปี":
    months = 12

# 📥 ดึงข้อมูลจากฐานข้อมูล
with st.spinner("⏳ กำลังดึงข้อมูลรีวิว..."):
    if months:
        df = get_reviews_by_period(
            platform=None if platform_option == "ทั้งหมด" else platform_option,
            months=months
        )
    else:
        df = get_all_reviews(
            platform=None if platform_option == "ทั้งหมด" else platform_option
        )

# 📊 แสดงข้อมูล
if df is not None and not df.empty:
    total_reviews = len(df)
    st.success(f"✅ พบรีวิวทั้งหมด {total_reviews:,} รายการ")

    # 🧠 สรุป sentiment
    if "sentiment" in df.columns:
        col1, col2, col3 = st.columns(3)
        positive = len(df[df["sentiment"] == "positive"])
        negative = len(df[df["sentiment"] == "negative"])
        neutral = len(df[df["sentiment"] == "neutral"])

        col1.metric("😊 รีวิวเชิงบวก", f"{positive:,}")
        col2.metric("😐 รีวิวกลางๆ", f"{neutral:,}")
        col3.metric("😠 รีวิวเชิงลบ", f"{negative:,}")

    # 📈 กราฟสรุป
    if show_chart and "review_date" in df.columns:
        st.divider()
        st.subheader("📅 แนวโน้มจำนวนรีวิวตามเวลา")

        try:
            df["review_date"] = pd.to_datetime(df["review_date"])
            df["month"] = df["review_date"].dt.to_period("M").astype(str)
            trend_df = df.groupby("month").size().reset_index(name="จำนวนรีวิว")

            fig = px.line(
                trend_df,
                x="month", y="จำนวนรีวิว",
                markers=True,
                title="แนวโน้มจำนวนรีวิวรายเดือน",
                color_discrete_sequence=["#1d4ed8"]
            )
            fig.update_layout(xaxis_title="เดือน", yaxis_title="จำนวนรีวิว")
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.warning(f"⚠️ ไม่สามารถสร้างกราฟได้: {e}")

    # 🧾 ตารางรีวิวทั้งหมด
    st.divider()
    st.subheader("📋 รายการรีวิวทั้งหมด")
    st.dataframe(
        df[["platform", "shop_id", "review_text", "sentiment", "review_date"]],
        use_container_width=True, height=550
    )

else:
    st.warning("⚠️ ไม่พบข้อมูลรีวิวในช่วงเวลาที่เลือก")
