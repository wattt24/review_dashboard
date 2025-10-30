#pages/admin_dashboard.py
import os
import sys
import pandas as pd
import numpy as np
import streamlit as st
from utils.config import SHOPEE_SHOP_ID
import altair as alt
import plotly.express as px
import matplotlib.pyplot as plt
from utils.token_manager import get_gspread_client
# from api.fujikaservice_rest_api import fetch_all_products_fujikaservice
from datetime import datetime, timedelta
from database.all_database import get_all_reviews, get_reviews_by_period
from database.all_database import get_connection
# from api.fujikaservice_rest_api import *
# from api.facebook_graph_api import get_page_info, get_page_posts, get_page_reviews
from api.line_oa_processing import fetch_line_messages, analyze_messages, summarize_categories, summarize_confidence
from utils.config import FACEBOOK_PAGE_HEATER_ID, FACEBOOK_PAGE_BBQ_ID
from services.gsc_fujikathailand import *  # ดึง DataFrame จากไฟล์ก่อนหน้า
st.set_page_config(page_title="Fujika Dashboard",page_icon="🌎", layout="wide")
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# from api.fujikathailand_rest_api import *
# from services.gsc_fujikathailand import *
from collections import defaultdict
# service_products = fetch_service_all_products()
# products = service_products 
# sales_data, buyers_list, total_orders = fetch_sales_and_buyers_all(order_status="completed")
import json

client = get_gspread_client()
sheet = client.open_by_key(os.environ["GOOGLE_SHEET_ID"] or st.secrets["GOOGLE_SHEET_ID"]).sheet1
def make_safe_for_streamlit(df):
    """แปลงทุก column object/list/dict เป็น string เพื่อให้ Streamlit แสดงได้"""
    for col in df.columns:
        if df[col].dtype == "object":
            df[col] = df[col].apply(lambda x: json.dumps(x) if isinstance(x, (list, dict)) else str(x))
    return df


st.title("📊 Dashboard's ข้อมูลจากหลายแพลตฟอร์ม")

view = st.selectbox("🔽 เลือกหน้าแสดงผล", ["Highlights Overview","Data Sources" ])


if view == "Highlights Overview":
        
        st.title("Highlights Overview")



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
                df["review_date"] = pd.to_datetime(df["review_date"])

                # กำหนดช่วงเวลาให้กราฟตาม period_option
                if period_option == "1 เดือน":
                    df["period"] = df["review_date"].dt.date.astype(str)  # รายวัน
                elif period_option == "3 เดือน":
                    df["period"] = df["review_date"].dt.to_period("W").astype(str)  # รายสัปดาห์
                elif period_option == "1 ปี":
                    df["period"] = df["review_date"].dt.to_period("M").astype(str)  # รายเดือน
                else:  # "ทั้งหมด"
                    df["period"] = df["review_date"].dt.to_period("Y").astype(str)  # รายปี

                trend_df = df.groupby("period").size().reset_index(name="จำนวนรีวิว")
                fig = px.line(
                    trend_df,
                    x="period", y="จำนวนรีวิว",
                    markers=True,
                    title="แนวโน้มจำนวนรีวิวตามเวลา",
                    color_discrete_sequence=["#1d4ed8"]
                )
                fig.update_layout(xaxis_title="ช่วงเวลา", yaxis_title="จำนวนรีวิว")
                st.plotly_chart(fig, use_container_width=True)

            # 🧾 ตารางรีวิวทั้งหมด + ปุ่ม Export
            display_df = df.rename(columns={
                "platform": "แพลตฟอร์ม",
                "shop_id": "รหัสร้านค้า",
                "review_text": "ข้อความรีวิว",
                "sentiment": "อารมณ์รีวิว",
                "review_date": "วันที่รีวิว"
            })       
            # ✅ เพิ่มคอลัมน์ลำดับที่เริ่มจาก 1
            display_df = display_df.copy()  # ป้องกัน SettingWithCopyWarning
            display_df.insert(0, "ลำดับ", range(1, len(display_df) + 1))

            # ✅ แสดงผล
           # 🔹 แปลงข้อความเป็น string
            for col in ["platform", "shop_id", "review_text", "rating", "sentiment", "review_date"]:
                if col in df.columns:
                    df[col] = df[col].fillna("").astype(str)

            # 🔹 toggle ตาราง
            show_table_time = st.toggle("👀 views", value=False , key= "show_table_time")
            if show_table_time:
                st.dataframe(
                    display_df[["ลำดับ", "แพลตฟอร์ม", "รหัสร้านค้า", "ข้อความรีวิว", "อารมณ์รีวิว", "วันที่รีวิว"]],
                    use_container_width=True,
                    height=550
                )

            # 🔹 ปุ่มดาวน์โหลด CSV
            csv_data = df[["platform", "shop_id", "review_text","rating",  "sentiment", "review_date"]].to_csv(
                index=False, encoding='utf-8-sig'
            )
            st.download_button(
                label="📥 ดาวน์โหลด",
                data=csv_data,
                file_name=f"review_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        

        else:
            st.warning("⚠️ ไม่พบข้อมูลรีวิวในช่วงเวลาที่เลือก")
        st.title("📊 Dashboard รีวิวหลาย Platform")

        #111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111

        # 🔽 ส่วนกรองข้อมูล
        with st.container():
            col1, col2, col3 = st.columns([1,1,1])

            with col1:
                period_option = st.selectbox(
                    "🕒 เลือกช่วงเวลา",
                    ("ทั้งหมด", "1 เดือน", "3 เดือน", "1 ปี"),
                    key="period_selectbox"
                )

            with col2:
                platform_option = st.selectbox(
                    "🌐 แพลตฟอร์ม",
                    ("ทั้งหมด", "fujikathailand", "FACEBOOK", "SHOPEE", "LAZADA", "LINE"),
                    key="platform_selectbox"
                )

            with col3:
                show_chart_graph = st.toggle("📈 แสดงกราฟสรุป", value=True, key="show_chart_toggle")

        # แปลงค่าช่วงเวลาเป็นเดือน
        months = None
        if period_option == "1 เดือน":
            months = 1
        elif period_option == "3 เดือน":
            months = 3
        elif period_option == "1 ปี":
            months = 12

        # แปลง platform "ทั้งหมด" เป็น None
        platform = None if platform_option == "ทั้งหมด" else platform_option

        # ---- ดึงข้อมูลจาก database ----
        if months is None and platform is None:
            df = get_all_reviews()
        elif months is None:
            df = get_all_reviews(platform=platform)
        else:
            df = get_reviews_by_period(platform=platform, months=months)

        if df.empty:
            st.warning("❌ ไม่มีข้อมูลรีวิว")
        else:

            if show_chart:
                df['review_date'] = pd.to_datetime(df['review_date'])

                fig = px.line(
                    df,
                    x='review_date',
                    y='rating',
                    color='platform',
                    labels={'review_date':'วันที่','rating':'Rating','platform':'Platform'},
                    title="📈 Rating  Platform",
                    markers=True,  # แสดงจุดของแต่ละรีวิวบนเส้น
                    hover_data=['review_text', 'shop_id', 'product_id']
                )

                fig.update_layout(
                    yaxis=dict(range=[0,5]),
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    legend_title_text='Platform'
                )

                st.plotly_chart(fig, use_container_width=True)


            # ---- ตารางรีวิว ----
            display_df = df.copy()
            display_df['review_date'] = pd.to_datetime(display_df['review_date'])
            display_df.sort_values(by='review_date', ascending=False, inplace=True)
            display_df.reset_index(drop=True, inplace=True)
            display_df['ลำดับ'] = display_df.index + 1

            display_df.rename(columns={
                'platform':'แพลตฟอร์ม',
                'shop_id':'รหัสร้านค้า',
                'product_id':'รหัสสินค้า',
                'review_id':'รหัสรีวิว',
                'rating':'คะแนน',
                'sentiment':'อารมณ์รีวิว',
                'review_text':'ข้อความรีวิว',
                'keywords':'คำสำคัญ',
                'review_date':'วันที่รีวิว'
            }, inplace=True)

            show_table_review = st.toggle("👀ตารางรีวิว", value=False, key="toggle_table_review")
            if show_table_review:
                st.dataframe(
                    display_df[["ลำดับ","แพลตฟอร์ม","รหัสร้านค้า","คะแนน","ข้อความรีวิว","อารมณ์รีวิว","วันที่รีวิว"]],
                    width='stretch',
                    height=550
                )

            # ---- ดาวน์โหลด CSV ----
            csv_data = display_df.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="📥 ดาวน์โหลด CSV",
                data=csv_data,
                file_name=f"reviews_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
            


        # ดึงข้อมูลทั้งหมด
        df = get_all_reviews()

        if df.empty:
            st.warning("ไม่มีข้อมูลรีวิวในฐานข้อมูล")
        else:
            # รวมจำนวนรีวิวต่อแพลตฟอร์ม และเรียงจากมากไปน้อย
            platform_counts = (
                df.groupby("platform")
                .size()
                .reset_index(name="จำนวนรีวิว")
                .sort_values("จำนวนรีวิว", ascending=False)
            )

            # ไอคอนแต่ละแพลตฟอร์ม
            platform_icons = {
                "Shopee": "🛒",
                "Lazada": "📦",
                "Facebook": "📘",
                "fujikathailand.com": "🌐",
                "cpsmanu.com": "🏭",
                "fujikaservice.com": "🔧"
            }

            # สีพื้นหลังของแต่ละแพลตฟอร์ม
            platform_colors = {
                "Shopee": "#FF6B00",          # ส้ม
                "Facebook": "#1877F2",        # น้ำเงินฟ้า
                "Lazada": "#7F3CFF",          # น้ำเงินม่วง
                "fujikathailand.com": "#FFD700",  # เหลืองทอง
                "cpsmanu.com": "#9ca3af",     # เทา
                "fujikaservice.com": "#34d399" # เขียวมิ้นท์
            }

            # 🌈 CSS สไตล์ใหม่ให้ดูเรียบหรูขึ้น
            st.markdown("""
            <style>
            .platform-container {
                display: flex;
                justify-content: flex-start;
                flex-wrap: nowrap;
                gap: 16px;
                overflow-x: auto;
                padding: 10px 5px 20px 5px;
            }
            .platform-card {
                min-width: 160px;
                height: 140px;
                border-radius: 16px;
                padding: 16px;
                text-align: center;
                color: white;
                font-family: "Segoe UI", sans-serif;
                box-shadow: 0 4px 10px rgba(0,0,0,0.15);
                transition: all 0.3s ease;
                flex-shrink: 0;
            }
            .platform-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 8px 16px rgba(0,0,0,0.2);
            }
            .icon {
                font-size: 30px;
                margin-bottom: 6px;
            }
            .platform-name {
                font-weight: 600;
                font-size: 16px;
            }
            .review-count {
                font-size: 18px;
                font-weight: bold;
                margin-top: 6px;
            }
            .rank-label {
                font-size: 13px;
                opacity: 0.9;
                margin-top: 3px;
            }
            </style>
            """, unsafe_allow_html=True)

            st.markdown("## 🏆 จัดอันดับจำนวนรีวิวจากทุกแพลตฟอร์ม")

            # แสดงการ์ด
            st.markdown('<div class="platform-container">', unsafe_allow_html=True)

            for idx, row in platform_counts.iterrows():
                platform = row["platform"]
                review_count = int(row["จำนวนรีวิว"])
                icon = platform_icons.get(platform, "💬")
                bg_color = platform_colors.get(platform, "#60a5fa")  # สีฟ้ามาตรฐานถ้าไม่พบ

                st.markdown(f"""
                <div class="platform-card" style="background:{bg_color};">
                    <div class="icon">{icon}</div>
                    <div class="platform-name">{platform}</div>
                    <div class="review-count">{review_count:,} รีวิว</div>
                    <div class="rank-label">อันดับ {idx+1}</div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)






        




elif view == "Data Sources":




        st.markdown("""
            <style>
                /* กล่องแท็บหลัก */
                div[data-baseweb="tab-list"] {
                    display: flex;
                    flex-wrap: wrap;
                    justify-content: center;
                    gap: 8px;
                    background-color: #e3f2fd !important;  /* 💙 สีฟ้าอ่อน */
                    border-radius: 15px;
                    padding: 10px;
                }

                /* ปุ่มแท็บทั้งหมด */
                button[data-baseweb="tab"] {
                    background-color: #ffffff;
                    border-radius: 10px;
                    padding: 10px 20px;
                    font-size: 0.9rem;
                    font-weight: 500;
                    color: #444;
                    border: 1px solid #ccc;
                    transition: all 0.25s ease-in-out;
                    flex: 1 1 auto;
                    min-width: 130px;
                    text-align: center;
                }

                /* Hover */
                button[data-baseweb="tab"]:hover {
                    background-color: #f1f9ff;
                    color: #007bff;
                    transform: scale(1.05);
                }

                /* Active Tab: เปลี่ยนสีตามลำดับแท็บ */
                /* 1 = Fujikathailand */
                div[data-baseweb="tab-list"] > button:nth-child(1)[aria-selected="true"] {
                    background: linear-gradient(135deg, #007bff, #00bcd4);
                    color: white;
                    font-weight: 600;
                }

                /* 2 = CPSManu */
                div[data-baseweb="tab-list"] > button:nth-child(2)[aria-selected="true"] {
                    background: linear-gradient(135deg, #5c6bc0, #7986cb);
                    color: white;
                    font-weight: 600;
                }

                /* 3 = FujikaService */
                div[data-baseweb="tab-list"] > button:nth-child(3)[aria-selected="true"] {
                    background: linear-gradient(135deg, #009688, #4db6ac);
                    color: white;
                    font-weight: 600;
                }

                /* 4 = Shopee */
                div[data-baseweb="tab-list"] > button:nth-child(4)[aria-selected="true"] {
                    background: linear-gradient(135deg, #ff7043, #ff5722);
                    color: white;
                    font-weight: 600;
                }

                /* 5 = Lazada */
                div[data-baseweb="tab-list"] > button:nth-child(5)[aria-selected="true"] {
                    background: linear-gradient(135deg, #1a73e8, #8e24aa);
                    color: white;
                    font-weight: 600;
                }

                /* 6 = Facebook */
                div[data-baseweb="tab-list"] > button:nth-child(6)[aria-selected="true"] {
                    background: linear-gradient(135deg, #1877f2, #3b5998);
                    color: white;
                    font-weight: 600;
                }

                /* 7 = LINE OA */
                div[data-baseweb="tab-list"] > button:nth-child(7)[aria-selected="true"] {
                    background: linear-gradient(135deg, #00b900, #00e676);
                    color: white;
                    font-weight: 600;
                }

                /* Responsive */
                @media (max-width: 768px) {
                    button[data-baseweb="tab"] {
                        font-size: 0.8rem;
                        padding: 8px 12px;
                        min-width: 100px;
                    }
                }

                @media (max-width: 480px) {
                    button[data-baseweb="tab"] {
                        font-size: 0.75rem;
                        padding: 6px 10px;
                        min-width: 85px;
                    }
                }
            </style>
        """, unsafe_allow_html=True)

        tabs = st.tabs([
            "📰 Fujikathailand.com",
            "🏭 CPSManu.com",
            "🛠️ FujikaService.com",
            "🛍️ Shopee",
            "🛒 Lazada",
            "📘 Facebook",
            "💬 LINE OA"
        ])



        # --------------------- 1. Fujikathailand ---------------------
        with tabs[0]:
            st.header("📰 Website Fujikathailand.com")
            st.set_page_config(page_title="Fujikathailand Reviews", layout="wide")
            # ---- เลือกช่วงเวลา ----
            st.markdown("""
            <style>
            /* กล่อง select ทั้งหมด */
            div[data-baseweb="select"] {
                background-color: #e0f2fe !important;
                border-radius: 6px !important;
                color: #1e3a8a !important;
            }

            /* ชั้นที่มีข้อความ */
            div[data-baseweb="select"] div[data-baseweb="value-container"] {
                color: #1e3a8a !important;
                font-weight: 600 !important;
                font-size: 15px !important;
                padding: 6px 10px !important;
                line-height: 1.6 !important;
                overflow: visible !important;
                white-space: normal !important;  /* ให้ text พับบรรทัดถ้ายาว */
            }

            /* ตัว dropdown ตอนเปิด */
            div[data-baseweb="menu"] {
                background-color: #f0f9ff !important;
                color: #1e3a8a !important;
                border-radius: 8px !important;
            }

            /* ตัวเลือกแต่ละรายการ */
            div[data-baseweb="option"] {
                color: #1e3a8a !important;
                font-size: 14px !important;
                padding: 8px 12px !important;
            }

            /* Hover */
            div[data-baseweb="option"]:hover {
                background-color: #bfdbfe !important;
                color: #1e3a8a !important;
            }
            </style>
            """, unsafe_allow_html=True )
            period_option = st.selectbox(
                "เลือกช่วงเวลาของรีวิว",
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

            
        # --------------------- 2. CPSManu ---------------------
        with tabs[1]:
            st.header("🏭 WordPress Posts: cpsmanu.com")
            st.write("ที่อยู่ ""https://www.cpsmanu.com/")
            st.title("สินค้าและบริการ")


            images = [
                {"url": "https://www.cpsmanu.com/wp-content/uploads/2023/02/icon-sh_gr.jpg", "link": "https://www.cpsmanu.com/water-heater/"},
                {"url": "https://www.cpsmanu.com/wp-content/uploads/2023/02/icon-pu_gr.jpg", "link": "https://www.cpsmanu.com/home-water-pump/"},
                {"url": "https://www.cpsmanu.com/wp-content/uploads/2023/02/icon-wa_gr.jpg", "link": "https://www.cpsmanu.com/water-purifier/"},
                {"url": "https://www.cpsmanu.com/wp-content/uploads/2023/02/icon-st_gr-.jpg", "link": "https://www.cpsmanu.com/electric-stove/"},
                {"url": "https://www.cpsmanu.com/wp-content/uploads/2023/02/icon-oem_gr.jpg", "link": "https://www.cpsmanu.com/oem-odm-services/"},
            ]

            cols = st.columns(len(images))

            for col, img in zip(cols, images):
                with col:
                    st.markdown(f'<a href="{img["link"]}" target="_blank"><img src="{img["url"]}" width="120" style="border-radius: 8px;"></a>', unsafe_allow_html=True)



        # --------------------- 3. FujikaService ---------------------
        
        with tabs[2]:
            
            # ===== ตั้งค่า Google Sheet =====
            SHEET_NAME = "Contact Information (Responses)"  # จาก Google Sheet ชื่อ "Contact Information (Responses)"
            # เรียกใช้งาน
            client = get_gspread_client()
            sheet = client.open(SHEET_NAME).sheet1
            rows = sheet.get_all_values()

            # ===== แปลงเป็น DataFrame =====
            df = pd.DataFrame(rows[1:], columns=rows[0])

            # ===== ลบ column ซ้ำ =====
            df = df.loc[:, ~df.columns.duplicated()]

            # ===== เลือกเฉพาะคอลัมน์ A–s (0–19) =====
            df_selected = df.iloc[:, :19]

            # ===== ทำความสะอาดค่า Model =====
            df_selected['Model'] = df_selected['Model'].str.strip()

            # ===== นับอันดับ Model =====
            model_series = df_selected['Model']
            model_counts = model_series.value_counts()
            top_models = model_counts.head(3)

            # ===== ตั้งค่า Streamlit Dashboard =====
            st.set_page_config(page_title="📊 Dashboard แบบสอบถาม", layout="wide")

            st.title("📊 Dashboard ข้อมูลบริการหลังขาย")
            # st.markdown(
            #     """
            #     <style>
            #     .stApp {
            #           /* สีพื้นหลัง */
            #     }
            #     </style>
            #     """,
            #     unsafe_allow_html=True
            # )
            st.markdown("""
            <div style="
                background-color: #f0f2f6;
            ">
            """, unsafe_allow_html=True)

            # ===== ตัวค้นหา Model =====
            st.subheader("🔍 ค้นหาอันดับ Model")

            st.markdown(
                """
                <style>
                textarea {
                    background-color: #ffffff !important;  /* พื้นหลังสีขาว */
                    color: #000000 !important;             /* ตัวอักษรสีดำ */
                    border: 2px solid #cccccc !important;  /* ขอบสีเทาอ่อน */
                    border-radius: 10px !important;
                    padding: 0px !important;

                }
                </style>
                """,
                unsafe_allow_html=True
            )

            search_model = st.text_area("ตรวจสอบ Model" , height=10)


            if search_model:
                search_model_clean = search_model.strip()

                if search_model_clean in df_selected['Model'].values:
                    rank = model_counts.index.get_loc(search_model_clean) + 1
                    count = model_counts[search_model_clean]

                    st.success(f"Model {search_model_clean} อยู่ในอันดับที่ {rank} (จำนวนคำสั่งซื้อ {count})")

                    with st.expander(f"📄 ดูรายละเอียดของ Model {search_model_clean}"):
                        # ดึงข้อมูลของ Model
                        model_data = df_selected[df_selected['Model'] == search_model_clean]

                        # เลือก column ที่ต้องการ
                        columns_to_show = ['Timestamp', 'Address - ที่อยู่', 'ช่องทางการสั่งซื้อ', 
                                        'ข้อเสนอแนะ ติชม', 'รู้จักเราทางไหน']
                        columns_exist = [col for col in columns_to_show if col in model_data.columns]
                        model_data_filtered = model_data[columns_exist]

                        # เปลี่ยนชื่อ column ให้เข้าใจง่าย
                        new_names = ["เวลา", "ที่อยู่", "ช่องทางการสั่งซื้อ", "ข้อเสนอแนะ ติชม", "รู้จักเราทางไหน"]
                        model_data_filtered.columns = new_names[:len(columns_exist)]

                        # แสดง DataFrame
                        st.dataframe(model_data_filtered)

                else:
                    st.warning(f"ไม่พบประวัติ {search_model_clean} ในข้อมูล")

            # ===== แสดง 3 อันดับ Model =====
            st.subheader("3 อันดับ Model ที่มียอดสั่งซื้อสูงสุด")
            st.bar_chart(top_models)

            st.markdown("---")

            if 'ช่องทางการสั่งซื้อ' in df_selected.columns:
                st.subheader("📊 จัดอันดับยอดคำสั่งซื้อตามช่องทางการสั่งซื้อ")

                # ====== 1. นับจำนวนแต่ละช่องทาง ======
                channel_counts = df_selected['ช่องทางการสั่งซื้อ'].value_counts().reset_index()
                channel_counts.columns = ['ช่องทาง', 'จำนวน']

                # ====== 2. เพิ่มคอลัมน์เปอร์เซ็นต์ ======
                total_orders = channel_counts['จำนวน'].sum()
                channel_counts['เปอร์เซ็นต์'] = (channel_counts['จำนวน'] / total_orders * 100).round(2)

                # ====== 3. หาค่าสูงสุดและต่ำสุด ======
                max_channel = channel_counts.iloc[0]
                min_channel = channel_counts.iloc[-1]

                # ====== 4. สร้างกราฟแท่ง ======
                bars = alt.Chart(channel_counts).mark_bar(size=25).encode(
                    x='จำนวน:Q',
                    y=alt.Y('ช่องทาง:N', sort='-x'),
                    color='ช่องทาง:N',
                    tooltip=['ช่องทาง', 'จำนวน', 'เปอร์เซ็นต์']
                )

                # ====== 5. เพิ่มตัวเลขเปอร์เซ็นต์บนแท่ง ======
                text = alt.Chart(channel_counts).mark_text(
                    align='left',
                    baseline='middle',
                    dx=3  # ระยะห่างจากแท่ง
                ).encode(
                    x='จำนวน:Q',
                    y=alt.Y('ช่องทาง:N', sort='-x'),
                    text=alt.Text('เปอร์เซ็นต์:Q', format='.2f')
                )

                # ====== 6. รวมแท่ง + ตัวเลข ======
                chart = (bars + text).properties(height=300)

                st.altair_chart(chart, use_container_width=True)

                # ====== 7. แสดงช่องทางมาก/น้อยสุด ======
                st.markdown(f"""
                <div style="
                    padding: 8px 12px; 
                    background-color:#d4edda; 
                    color:#155724; 
                    border-radius:5px; 
                    width: fit-content;
                    display:inline-block;
                    margin-bottom:5px;
                    font-size:14px;
                ">
                📈 ยอดคำสั่งซื้อมากที่สุด <b>{max_channel['ช่องทาง']}</b> ({max_channel['จำนวน']} ครั้ง, {max_channel['เปอร์เซ็นต์']}%)
                </div>
                """, unsafe_allow_html=True)

                st.markdown(f"""
                <div style="
                    padding: 8px 12px; 
                    background-color:#fff3cd; 
                    color:#856404; 
                    border-radius:5px; 
                    width: fit-content;
                    display:inline-block;
                    font-size:14px;
                ">
                📉 ยอดคำสั่งซื้อน้อยที่สุด <b>{min_channel['ช่องทาง']}</b> ({min_channel['จำนวน']} ครั้ง, {min_channel['เปอร์เซ็นต์']}%)
                </div>
                """, unsafe_allow_html=True)


            st.markdown("----")
            st.markdown("---")
            if 'รู้จักเราทางไหน' in df_selected.columns:
                st.subheader("📊 ผลการตรวจสอบว่ารู้จักเราจากช่องทางไหน")

                know_counts = df_selected['รู้จักเราทางไหน'].value_counts().reset_index()
                know_counts.columns = ['ช่องทาง', 'จำนวน']

                fig = px.pie(
                    know_counts,
                    names='ช่องทาง',
                    values='จำนวน',
                    color='ช่องทาง',
                    color_discrete_sequence=px.colors.qualitative.Set3,
                    hole=0.4  # ทำเป็น donut chart
                )
                st.plotly_chart(fig, use_container_width=True)



            st.subheader("📄 ข้อเสนอแนะ ติชมทั้งหมด")

            # กรองเฉพาะแถวที่มีข้อเสนอแนะ
            df_feedback = df_selected[
                df_selected['ข้อเสนอแนะ ติชม'].notna() & 
                (df_selected['ข้อเสนอแนะ ติชม'].str.strip() != "") &
                (df_selected['ข้อเสนอแนะ ติชม'].str.strip() != "-")
            ].copy()  # copy เพื่อไม่ให้ warning

            # เพิ่มลำดับ
            df_feedback.insert(0, 'ลำดับ', range(1, len(df_feedback)+1))

            # แสดง DataFrame พร้อม 'ช่องทางการสั่งซื้อ'
            columns_to_show = ['ลำดับ', 'Model', 'ช่องทางการสั่งซื้อ', 'ข้อเสนอแนะ ติชม']
            st.dataframe(df_feedback[columns_to_show])

            # นับจำนวนข้อเสนอแนะต่อ Model
            feedback_counts = df_feedback.groupby('Model').size().reset_index(name='จำนวนข้อเสนอแนะ')
            total_feedback = len(df_feedback)
            st.markdown(f"จำนวนข้อเสนอแนะทั้งหมด: {total_feedback} รายการ")
            st.markdown("</div>", unsafe_allow_html=True)

           
        with tabs[3]:
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
            st.header("🛍️ รีวิว Shopee")
            period_option = st.selectbox(
                "🕒 เลือกช่วงเวลา",
                ("ทั้งหมด", "1 เดือน", "3 เดือน", "1 ปี")
            )

            # แปลงค่าช่วงเวลาเป็นเดือน
            months = None
            if period_option == "1 เดือน":
                months = 1
            elif period_option == "3 เดือน":
                months = 3
            elif period_option == "1 ปี":
                months = 12

            # 📥 ดึงข้อมูล Shopee จากฐานข้อมูล
            with st.spinner("⏳ กำลังดึงข้อมูลรีวิว Shopee..."):
                if months:
                    df = get_reviews_by_period(platform="shopee", months=months)
                else:
                    df = get_all_reviews(platform="shopee")

            # 📊 แสดงผลเหมือน Dashboard ปกติ
            if df is not None and not df.empty:
                total_reviews = len(df)
                st.success(f"✅ พบรีวิว Shopee ทั้งหมด {total_reviews:,} รายการ")

                # สรุป sentiment
                if "sentiment" in df.columns:
                    col1, col2, col3 = st.columns(3)
                    positive = len(df[df["sentiment"] == "positive"])
                    negative = len(df[df["sentiment"] == "negative"])
                    neutral = len(df[df["sentiment"] == "neutral"])

                    col1.metric("😊 รีวิวเชิงบวก", f"{positive:,}")
                    col2.metric("😐 รีวิวกลางๆ", f"{neutral:,}")
                    col3.metric("😠 รีวิวเชิงลบ", f"{negative:,}")

                # กราฟแนวโน้ม
                if "review_date" in df.columns:
                    df["review_date"] = pd.to_datetime(df["review_date"])
                    if period_option == "1 เดือน":
                        df["period"] = df["review_date"].dt.date.astype(str)
                    elif period_option == "3 เดือน":
                        df["period"] = df["review_date"].dt.to_period("W").astype(str)
                    elif period_option == "1 ปี":
                        df["period"] = df["review_date"].dt.to_period("M").astype(str)
                    else:
                        df["period"] = df["review_date"].dt.to_period("Y").astype(str)

                    trend_df = df.groupby("period").size().reset_index(name="จำนวนรีวิว")
                    fig = px.line(
                        trend_df,
                        x="period", y="จำนวนรีวิว",
                        markers=True,
                        title="แนวโน้มจำนวนรีวิว Shopee",
                        color_discrete_sequence=["#1d4ed8"]
                    )
                    fig.update_layout(xaxis_title="ช่วงเวลา", yaxis_title="จำนวนรีวิว")
                    st.plotly_chart(fig, use_container_width=True)

                # ตารางรีวิว + ดาวน์โหลด CSV
                display_df = df.rename(columns={
                    "platform": "แพลตฟอร์ม",
                    "shop_id": "รหัสร้านค้า",
                    "review_text": "ข้อความรีวิว",
                    "sentiment": "อารมณ์รีวิว",
                    "review_date": "วันที่รีวิว"
                })
                display_df.insert(0, "ลำดับ", range(1, len(display_df) + 1))

                show_table = st.toggle("👀 ดูตารางรีวิว", value=False, key="toggle_shopee_01")
                if show_table:
                    st.dataframe(
                        display_df[["ลำดับ", "แพลตฟอร์ม", "รหัสร้านค้า", "ข้อความรีวิว", "อารมณ์รีวิว", "วันที่รีวิว"]],
                        use_container_width=True,
                        height=550
                    )

                csv_data = df[["platform", "shop_id", "review_text","rating","sentiment","review_date"]].to_csv(
                    index=False, encoding='utf-8-sig'
                )
                st.download_button(
                    label="📥 ดาวน์โหลด CSV",
                    data=csv_data,
                    file_name=f"shopee_review_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            else:
                st.warning("⚠️ ไม่พบข้อมูลรีวิว Shopee ในช่วงเวลาที่เลือก")


                
        # --------------------- 5. Lazada ---------------------
        with tabs[4]:
            st.header("📦 Lazada reviews")

            with st.container():
                col1, col2 = st.columns([1,1])

                with col1:
                    period_option = st.selectbox(
                        "🕒 เลือกช่วงเวลา",
                        ("ทั้งหมด", "1 เดือน", "3 เดือน", "1 ปี"),
                        key="select_period_lazada"
                    )

                with col2:
                    show_chart = st.toggle("📈 แสดงกราฟสรุป", value=True, key="toggle_show_chart_lazada")

            # แปลงช่วงเวลาเป็นเดือน
            months = None
            if period_option == "1 เดือน":
                months = 1
            elif period_option == "3 เดือน":
                months = 3
            elif period_option == "1 ปี":
                months = 12

            # 📥 ดึงข้อมูลจากฐานข้อมูลเฉพาะ Lazada
            with st.spinner("⏳ กำลังดึงข้อมูลรีวิว Lazada..."):
                if months:
                    df = get_reviews_by_period(platform="LAZADA", months=months)
                else:
                    df = get_all_reviews(platform="LAZADA")

            # 📊 แสดงข้อมูล
            if df is not None and not df.empty:
                total_reviews = len(df)
                st.success(f"✅ พบรีวิว Lazada ทั้งหมด {total_reviews:,} รายการ")

                # 🧠 สรุป sentiment
                if "sentiment" in df.columns:
                    col1, col2, col3 = st.columns(3)
                    positive = len(df[df["sentiment"] == "positive"])
                    negative = len(df[df["sentiment"] == "negative"])
                    neutral = len(df[df["sentiment"] == "neutral"])

                    col1.metric("😊 รีวิวเชิงบวก", f"{positive:,}")
                    col2.metric("😐 รีวิวกลางๆ", f"{neutral:,}")
                    col3.metric("😠 รีวิวเชิงลบ", f"{negative:,}")

                # 📈 กราฟแนวโน้ม
                if show_chart and "review_date" in df.columns:
                    df["review_date"] = pd.to_datetime(df["review_date"])
                    if period_option == "1 เดือน":
                        df["period"] = df["review_date"].dt.date.astype(str)
                    elif period_option == "3 เดือน":
                        df["period"] = df["review_date"].dt.to_period("W").astype(str)
                    elif period_option == "1 ปี":
                        df["period"] = df["review_date"].dt.to_period("M").astype(str)
                    else:
                        df["period"] = df["review_date"].dt.to_period("Y").astype(str)

                    trend_df = df.groupby("period").size().reset_index(name="จำนวนรีวิว")
                    fig = px.line(
                        trend_df,
                        x="period", y="จำนวนรีวิว",
                        markers=True,
                        title="แนวโน้มจำนวนรีวิว Lazada ตามเวลา",
                        color_discrete_sequence=["#1d4ed8"]
                    )
                    fig.update_layout(xaxis_title="ช่วงเวลา", yaxis_title="จำนวนรีวิว")
                    st.plotly_chart(fig, use_container_width=True)

                # 🧾 ตารางรีวิวทั้งหมด + ปุ่มดาวน์โหลด CSV
                display_df = df.rename(columns={
                    "platform": "แพลตฟอร์ม",
                    "shop_id": "รหัสร้านค้า",
                    "review_text": "ข้อความรีวิว",
                    "sentiment": "อารมณ์รีวิว",
                    "review_date": "วันที่รีวิว"
                })
                display_df.insert(0, "ลำดับ", range(1, len(display_df) + 1))

                show_table = st.toggle("👀 ดูตารางรีวิว Lazada", value=False, key="toggle_show_table_lazada")
                if show_table:
                    st.dataframe(
                        display_df[["ลำดับ", "แพลตฟอร์ม", "รหัสร้านค้า", "ข้อความรีวิว", "อารมณ์รีวิว", "วันที่รีวิว"]],
                        use_container_width=True,
                        height=550
                    )

                # ปุ่มดาวน์โหลด CSV
                csv_data = df[["platform", "shop_id", "review_text", "rating", "sentiment", "review_date"]].to_csv(
                    index=False, encoding='utf-8-sig'
                )
                st.download_button(
                    label="📥 ดาวน์โหลด",
                    data=csv_data,
                    file_name=f"lazada_review_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )

            else:
                st.warning("⚠️ ไม่พบข้อมูลรีวิว Lazada ในช่วงเวลาที่เลือก")

        # --------------------- 6. Facebook Page / Ads ---------------------
        with tabs[5]:
            import time
            st.title("Facebook Page ")
            st.header("review เตาไฟฟ้าฟูจิก้า")
            with st.spinner("🔍 กำลังดึงข้อมูลจากฐานข้อมูล... กรุณารอสักครู่"):
                time.sleep(10)  # ให้หมุนค้างไว้ 10 วินาที

            st.success("✅ ดึงข้อมูลเสร็จเรียบร้อย!")



        # --------------------- 7. LINE OA ---------------------
        with tabs[6]:
            st.header("💬 LINE OA ")

            st.info("โหลดข้อความจากฐานข้อมูลและวิเคราะห์หมวดหมู่โดยโมเดล")

            # ดึงข้อมูล
            df_messages = fetch_line_messages()
            st.write(f"ตอนนี้มีข้อมูลจาก line messages {len(df_messages)} รายการ")

            # ปุ่มวิเคราะห์
            with st.spinner("🔍 กำลังวิเคราะห์ข้อความ..."):
                df_analyzed = analyze_messages(df_messages)

            # แสดงผลในตาราง scrollable
            
            # st.success("✅ วิเคราะห์เสร็จแล้ว")
            category_summary = summarize_categories(df_analyzed)
            # สร้าง pie chart
            fig_category = px.pie(
                category_summary,
                names="Category",
                values="Count",
                title="📊 สัดส่วนข้อความตาม Category",
                color_discrete_sequence=px.colors.qualitative.Set2
            )
            st.plotly_chart(fig_category, use_container_width=True)

            # สรุปความมั่นใจของโมเดล
            confidence_summary = summarize_confidence(df_analyzed)
            # สร้าง bar chart
            fig_confidence = px.bar(
                confidence_summary,
                x="category",
                y="ความมั่นใจเฉลี่ย",
                color="category",
                text="ความมั่นใจเฉลี่ย",
                title="📊 ความมั่นใจเฉลี่ยของโมเดลตาม Category",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig_confidence.update_traces(textposition='outside')
            fig_confidence.update_layout(yaxis=dict(range=[0,1]))
            st.plotly_chart(fig_confidence, use_container_width=True)

            # แสดง DataFrame ของข้อความทั้งหมด
            st.subheader("📋 ตารางข้อความที่วิเคราะห์แล้ว")
            st.dataframe(
                df_analyzed[["message", "category", "confidence"]].sort_values(by="confidence", ascending=False),
                height=600
            )