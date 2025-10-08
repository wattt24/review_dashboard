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

    # 🧾 ตารางรีวิวทั้งหมด + ปุ่ม Export
    st.divider()
    st.subheader("📋 รายการรีวิวทั้งหมด")
    st.dataframe(
        df[["platform", "shop_id", "review_text", "sentiment", "review_date"]],
        use_container_width=True, height=550
    )

    # 💾 ปุ่ม Export
    csv_data = df[["platform", "shop_id", "review_text", "sentiment", "review_date"]].to_csv(index=False, encoding='utf-8-sig')
    st.download_button(
        label="📥 ดาวน์โหลดรายงาน CSV",
        data=csv_data,
        file_name=f"review_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )

else:
    st.warning("⚠️ ไม่พบข้อมูลรีวิวในช่วงเวลาที่เลือก")

if "platform" in df.columns:
    st.divider()
    st.subheader("📊 จำนวนรีวิวตามแพลตฟอร์ม")
    platform_df = df.groupby("platform").size().reset_index(name="จำนวนรีวิว")
    platform_df = platform_df.sort_values(by="จำนวนรีวิว", ascending=False)

    # กราฟอันดับแพลตฟอร์ม


# 📊 Top Platform (แพลตฟอร์มที่มีรีวิวเยอะที่สุด)

if "platform" in df.columns:
    platform_df = df.groupby("platform").size().reset_index(name="จำนวนรีวิว")
    platform_df = platform_df.sort_values(by="จำนวนรีวิว", ascending=False)
    top_platforms = platform_df.head(3)  # Top 3

    st.divider()
    st.subheader("🏆 Top 3 แพลตฟอร์มที่มีรีวิวเยอะที่สุด")

    # กำหนดสี gradient แต่ละอันดับ
    gradients = [
        "linear-gradient(135deg, #4f46e5, #3b82f6)",  # อันดับ 1
        "linear-gradient(135deg, #10b981, #06b6d4)",  # อันดับ 2
        "linear-gradient(135deg, #f472b6, #f59e0b)"   # อันดับ 3
    ]

    cols = st.columns(3)
    for i, (index, row) in enumerate(top_platforms.iterrows()):
        with cols[i]:
            st.markdown(f"""
            <div style="
                background: {gradients[i]};
                color: white;
                padding: 25px;
                border-radius: 20px;
                text-align: center;
                box-shadow: 0 8px 20px rgba(0,0,0,0.2);
            ">
                <h2 style="margin: 0; font-size: 36px; font-weight: bold;">{i+1}. {row['platform'].upper()}</h2>
                <p style="margin: 5px 0 0; font-size: 22px; font-weight: 500;">{row['จำนวนรีวิว']:,} รีวิว</p>
            </div>
            """, unsafe_allow_html=True)


