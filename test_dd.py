# from database.all_database import get_connection
import streamlit as st
import streamlit as st
import plotly.express as px
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from itertools import chain

import pandas as pd
import pymysql
from collections import Counter
from itertools import chain
import json

def get_lazada_keywords_summary(limit_top=20):
    """
    ดึงข้อมูล Keywords จากรีวิว Lazada
    กรอง review_text ที่เป็น None/ว่างออก
    Returns:
        df_reviews: ตารางรีวิว (review_text, rating, keywords)
        df_top_keywords: top N keywords และจำนวนครั้ง
    """
    try:
        conn = pymysql.connect(
            host="yamanote.proxy.rlwy.net",
            user="root",
            password="yeiIByLVJqRlPrzKLGaNCNySevvHeabG",
            port=49296,
            database="railway",
            charset="utf8mb4"
        )

        query = """
        SELECT review_text, rating, keywords
        FROM reviews_history
        WHERE platform='lazada'
        """
        df = pd.read_sql(query, conn)
        conn.close()

        if df.empty:
            print("⚠️ ไม่มีข้อมูล Lazada")
            return pd.DataFrame(), pd.DataFrame()

        # =============================
        # กรอง review_text ที่ None หรือว่าง
        # =============================
        df = df[df['review_text'].notna()]
        df = df[df['review_text'].str.strip() != ""]

        if df.empty:
            print("⚠️ ไม่มี review_text ที่ใช้ได้")
            return pd.DataFrame(), pd.DataFrame()

        # =============================
        # แปลง keywords เป็น list และกรอง None/''/NaN
        # =============================
        def parse_keywords(k):
            if pd.isna(k):
                return []
            if isinstance(k, str):
                try:
                    v = json.loads(k)
                    if isinstance(v, list):
                        return [kw for kw in v if kw and kw != 'None']
                    elif isinstance(v, dict):
                        return [kw for kw in v.values() if kw and kw != 'None']
                    else:
                        return [k] if k and k != 'None' else []
                except:
                    return [k] if k and k != 'None' else []
            elif isinstance(k, list):
                return [kw for kw in k if kw and kw != 'None']
            return []

        df['keywords'] = df['keywords'].apply(parse_keywords)

        # =============================
        # Top Keywords
        # =============================
        all_keywords = list(chain.from_iterable(df['keywords']))
        counter = Counter(all_keywords)
        df_top_keywords = pd.DataFrame(counter.most_common(limit_top), columns=['Keyword','Count'])

        return df, df_top_keywords

    except Exception as e:
        print(f"❌ Error: {e}")
        return pd.DataFrame(), pd.DataFrame()



# def get_lazada_rating_summary():
#     try:
#         conn = pymysql.connect(
#             host="yamanote.proxy.rlwy.net",
#             user="root",
#             password="yeiIByLVJqRlPrzKLGaNCNySevvHeabG",
#             port=49296,
#             database="railway",
#             charset="utf8mb4"
#         )

#         query = """
#         SELECT rating, review_text, review_date
#         FROM reviews_history
#         WHERE platform = 'lazada' AND rating IS NOT NULL
#         """
#         df = pd.read_sql(query, conn)
#         conn.close()

#         if df.empty:
#             return pd.DataFrame(columns=["Rating", "Count"])

#         rating_counts = df['rating'].value_counts().reset_index()
#         rating_counts.columns = ["Rating", "Count"]
#         rating_counts["Avg_Review_Length"] = rating_counts["Rating"].apply(
#             lambda r: df[df['rating']==r]['review_text'].str.len().mean()
#         )
#         return rating_counts

#     except Exception as e:
#         print(f"❌ Error: {e}")
#         return pd.DataFrame(columns=["Rating", "Count"])


# st.header("📊 รีวิว Lazada")
# rating_summary = get_lazada_rating_summary()

# if rating_summary.empty:
#     st.warning("⚠️ ไม่มีข้อมูล Lazada ในฐานข้อมูล")
# else:
#     st.subheader("จำนวนรีวิวแต่ละระดับดาว")  

#     # =========================
#     # กำหนด custom order และสี
#     # =========================
#     custom_order = [5, 3, 4, 2, 1]
#     color_map = {
#         '5': "#2ca02c",
#         '3': "#ff7f0e",
#         '4': "#9467bd",
#         '2': "#d06969",
#         '1': "#1f77b4"
#     }

#     # แปลง Rating เป็น string
#     rating_summary['Rating_str'] = rating_summary['Rating'].astype(str)

#     # สร้างกราฟ
#     fig = px.bar(
#         rating_summary,
#         x='Rating_str',
#         y='Count',
#         text='Count',
#         hover_data=['Avg_Review_Length'],
#         color='Rating_str',  # ใช้ column string ทั้ง x และ color
#         color_discrete_map=color_map,
#         category_orders={"Rating_str": [str(r) for r in custom_order]},
#         title="จำนวนรีวิวต่อระดับดาว - Lazada"
#     )

#     fig.update_traces(textposition='outside')
#     fig.update_layout(
#         xaxis_title="ระดับดาว (Rating)",
#         yaxis_title="จำนวนรีวิว",
#         title_x=0.5,
#         showlegend=False
#     )

#     st.plotly_chart(fig, use_container_width=True)

# เรียกฟังก์ชัน
df_reviews, df_top_keywords = get_lazada_keywords_summary(limit_top=20)

if df_reviews.empty:
    st.warning("⚠️ ไม่มีข้อมูล Lazada")
else:
    st.subheader("1️⃣ ตารางรีวิว")
    st.dataframe(df_reviews[['review_text','rating','keywords']])

    st.subheader("2️⃣ Top Keywords (Table + Bar Chart)")
    st.dataframe(df_top_keywords)

    fig1 = px.bar(df_top_keywords, x='Keyword', y='Count', title="Top 20 Keywords")
    st.plotly_chart(fig1, use_container_width=True)
