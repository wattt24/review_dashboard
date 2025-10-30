
# import streamlit as st
# from utils.config import FACEBOOK_PAGE_HEATER_ID, FACEBOOK_PAGE_BBQ_ID
# from api.facebook_graph_api import get_page_info, get_page_posts, get_page_reviews


# # ============================ ส่วนฟังก์ชัน UI ============================

# def render_page_info(page_info, page_id):#แสดงข้อมูลเพจ (ชื่อ โลโก้ ID)
#     if "error" in page_info:
#         st.error(f"❌ Facebook API error: {page_info['error']}")
#         return

#     name = page_info.get("name", "ไม่ทราบชื่อเพจ")
#     picture = page_info.get("picture", {}).get("data", {}).get("url", "")

#     st.markdown(
#         f"""
#         <div style="
#             background-color:#f9f9f9;
#             padding:20px;
#             border-radius:15px;
#             text-align:center;
#             box-shadow:2px 2px 8px rgba(0,0,0,0.1);
#             margin-bottom:20px;">
#             <img src="{picture}" width="80" style="border-radius:50%;">
#             <h3 style="margin:10px 0;">{name}</h3>
#             <p>Page ID: {page_id}</p>
#         </div>
#         """,
#         unsafe_allow_html=True
#     )

# def render_page_posts(posts, num_posts: int):
#     """แสดงโพสต์ล่าสุด"""
#     st.subheader(f"📝 โพสต์ล่าสุด {num_posts} โพสต์")
#     if not posts:
#         st.info("ไม่มีโพสต์ให้แสดง")
#         return

#     for post in posts:
#         message = post.get("message", "(ไม่มีข้อความ)")[:100]
#         st.markdown(f"- [{message}...]({post['permalink_url']}) - {post['created_time']}")


# def render_page_reviews(reviews, num_reviews: int):
#     """แสดงรีวิวล่าสุด"""
#     st.subheader(f"⭐ รีวิวล่าสุด {num_reviews} รายการ")
#     if not reviews:
#         st.info("ยังไม่มีรีวิวสำหรับเพจนี้")
#         return

#     for r in reviews:
#         reviewer = r.get("reviewer", {}).get("name", "Anonymous")
#         rating_type = r.get("recommendation_type", "")
#         review_text = r.get("review_text", "")
#         created_time = r.get("created_time", "")
#         st.markdown(f"- **{reviewer}** | {rating_type} | {review_text} | {created_time}")


# # ============================ ส่วนแสดงผลหลัก (Main App) ============================

# st.title("📘 Facebook Pages Overview")

# for page_id in [FACEBOOK_PAGE_HEATER_ID, FACEBOOK_PAGE_BBQ_ID]:
#     page_info = get_page_info(page_id)
#     render_page_info(page_info, page_id)

#     posts = get_page_posts(page_id, limit=3)
#     render_page_posts(posts, num_posts=3)

#     reviews = get_page_reviews(page_id, limit=5)
#     render_page_reviews(reviews, num_reviews=5)

# ฟรี 100% ใช้ HuggingFace
# from transformers import pipeline
# import pandas as pd
# import psycopg2

# import plotly.express as px
# import streamlit as st
# from database.all_database import get_connection
# import pandas as pd
# from database.all_database import get_connection

# def inspect_line_messages(limit=10):
#     conn = get_connection()
#     query = f"SELECT * FROM line_messages ORDER BY created_at DESC LIMIT {limit};"
#     df = pd.read_sql(query, conn)
#     conn.close()

#     print("🧱 คอลัมน์ทั้งหมดใน line_messages:")
#     print(df.columns.tolist())
#     print("\n📊 ตัวอย่างข้อมูล:")
#     print(df.head())

#     print(f"\nรวมทั้งหมด {len(df)} แถว")
#     return df
# def fetch_line_messages(limit=50):
#     conn = get_connection()
#     query = f"""
#         SELECT id, user_id, message, created_at
#         FROM line_messages
#         WHERE message_type = 'text'
#           AND direction = 'user'
#           AND message IS NOT NULL
#         ORDER BY created_at DESC
#         LIMIT {limit};
#     """
#     df = pd.read_sql(query, conn)
#     conn.close()
#     print(f"✅ ดึงข้อมูลมาแล้ว {len(df)} ข้อความ")
#     return df

# def check_unique_values():
#     conn = get_connection()
#     df = pd.read_sql("SELECT message_type, direction, COUNT(*) FROM line_messages GROUP BY message_type, direction;", conn)
#     conn.close()
#     print(df)
#     return df
# # ==========================
# # 2️⃣ โหลดโมเดลสำหรับจัดหมวดหมู่
# # ==========================
# def get_classifier():
#     print("📦 กำลังโหลดโมเดล zero-shot classification...")
#     return pipeline("zero-shot-classification", model="MoritzLaurer/mDeBERTa-v3-base-mnli-xnli")




# # ==========================
# # 3️⃣ ฟังก์ชันจัดประเภทข้อความ
# # ==========================
# def classify_message(text, classifier):
#     labels = ["คำถาม", "รีวิวสินค้า", "คำชม", "ร้องเรียน", "สอบถามบริการ", "อื่นๆ"]
#     try:
#         result = classifier(text, candidate_labels=labels, multi_label=False)
#         if result and "labels" in result and "scores" in result:
#             return result["labels"][0], float(result["scores"][0])
#         else:
#             return "อื่นๆ", 0.0
#     except Exception as e:
#         print(f"⚠️ classify_message error: {e}")
#         return "อื่นๆ", 0.0


# # ==========================
# # 4️⃣ วิเคราะห์ข้อความทั้งหมด
# # ==========================
# def analyze_messages(df):
#     if df.empty:
#         df["category"] = []
#         df["confidence"] = []
#         return df

#     classifier = get_classifier()
#     results = [classify_message(x, classifier) for x in df["message"]]
#     df["category"], df["confidence"] = zip(*results)
#     return df


# def analyze_and_display_all():
#     df = fetch_line_messages()
#     if df.empty:
#         print("❌ ไม่มีข้อความให้วิเคราะห์")
#         return
    
#     classifier = get_classifier()
#     print("🔍 กำลังวิเคราะห์ข้อความ...")

#     results = [classify_message(msg, classifier) for msg in df["message"]]
#     df["category"], df["confidence"] = zip(*results)
    
#     print("✅ วิเคราะห์เสร็จแล้ว")
#     # แสดงผลทุกแถว
#     pd.set_option("display.max_rows", None)  # แสดงทุกแถว
#     pd.set_option("display.max_colwidth", None)  # แสดงข้อความเต็ม
#     print(df[["message", "category", "confidence"]])

# def summarize_categories(df):
#     summary = df["category"].value_counts().reset_index()
#     summary.columns = ["Category", "Count"]
#     summary["Percent"] = (summary["Count"] / len(df) * 100).round(2)
#     return summary

# def summarize_confidence(df):
#     summary = df.groupby("category")["confidence"].agg(
#         ['count', 'mean', 'max']
#     ).sort_values(by="mean", ascending=False).reset_index()
#     summary.rename(columns={
#         "count": "จำนวนข้อความ",
#         "mean": "ความมั่นใจเฉลี่ย",
#         "max": "ความมั่นใจสูงสุด"
#     }, inplace=True)
#     summary["ความมั่นใจเฉลี่ย"] = summary["ความมั่นใจเฉลี่ย"].round(3)
#     summary["ความมั่นใจสูงสุด"] = summary["ความมั่นใจสูงสุด"].round(3)
#     return summary


# if __name__ == "__main__":
    # # check_unique_values()
    # inspect_line_messages(10)
    # analyzed_df = analyze_messages(10)
    # print("🎯 ตัวอย่างผลลัพธ์:")
    # print(analyzed_df[["message", "category", "confidence"]].head())
    # inspect_line_messages(10)
    
    # # 2. ดูจำนวนข้อความตามประเภท
    # check_unique_values()
    
    # # 3. วิเคราะห์ข้อความ
    # analyzed_df = analyze_messages(34)
    
    # 4. แสดงผลลัพธ์
    # print("🎯 ตัวอย่างผลลัพธ์:")
    # print(analyzed_df[["message", "category", "confidence"]].head())
    # print(analyzed_df.loc[10:15, ["message", "category", "confidence"]])
    # analyze_and_display_all()



    # st.title("📊 LINE Messages Dashboard")

    # st.info("โหลดข้อความจากฐานข้อมูลและวิเคราะห์หมวดหมู่โดยโมเดล")

    # # ดึงข้อมูล
    # df_messages = fetch_line_messages()
    # st.write(f"ตอนนี้มีข้อมูลจาก line messages {len(df_messages)} รายการ")

    # # ปุ่มวิเคราะห์
    # with st.spinner("🔍 กำลังวิเคราะห์ข้อความ..."):
    #     df_analyzed = analyze_messages(df_messages)

    # # แสดงผลในตาราง scrollable
    
    # st.success("✅ วิเคราะห์เสร็จแล้ว")
    # category_summary = summarize_categories(df_analyzed)
    # # สร้าง pie chart
    # fig_category = px.pie(
    #     category_summary,
    #     names="Category",
    #     values="Count",
    #     title="📊 สัดส่วนข้อความตาม Category",
    #     color_discrete_sequence=px.colors.qualitative.Set2
    # )
    # st.plotly_chart(fig_category, use_container_width=True)

    # # สรุปความมั่นใจของโมเดล
    # confidence_summary = summarize_confidence(df_analyzed)
    # # สร้าง bar chart
    # fig_confidence = px.bar(
    #     confidence_summary,
    #     x="category",
    #     y="ความมั่นใจเฉลี่ย",
    #     color="category",
    #     text="ความมั่นใจเฉลี่ย",
    #     title="📊 ความมั่นใจเฉลี่ยของโมเดลตาม Category",
    #     color_discrete_sequence=px.colors.qualitative.Set3
    # )
    # fig_confidence.update_traces(textposition='outside')
    # fig_confidence.update_layout(yaxis=dict(range=[0,1]))
    # st.plotly_chart(fig_confidence, use_container_width=True)

    # # แสดง DataFrame ของข้อความทั้งหมด
    # st.subheader("📋 ตารางข้อความที่วิเคราะห์แล้ว")
    # st.dataframe(
    #     df_analyzed[["message", "category", "confidence"]].sort_values(by="confidence", ascending=False),
    #     height=600
    # )

# -*- coding: utf-8 -*-
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import torch.nn.functional as F

# โหลดโมเดลและ tokenizer
model_name = "FlukeTJ/distilbert-base-thai-sentiment"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)

def analyze_sentiment(text: str):
    inputs = tokenizer(text[:512], return_tensors="pt")  # ตัด 512 token
    # ลบ token_type_ids หากมี
    if "token_type_ids" in inputs:
        del inputs["token_type_ids"]
    
    outputs = model(**inputs)
    probs = F.softmax(outputs.logits, dim=-1)
    labels = ["negative", "neutral", "positive"]
    idx = torch.argmax(probs, dim=-1).item()
    return labels[idx], probs[0, idx].item()

# ทดสอบ


# 🔹 ตัวอย่างการใช้งาน
if __name__ == "__main__":
 
    text = "ใช้ดีจ้า ซื้อเป็นครั้งที่สองแล้ว ดีว่าเก็บโคดสำเร็จ แถมส่งฟรี ปิ้งเหมือนไปกินบาบีก้อน แต่วุกไม่ทันใจคนเยอะ กินได้ประมาณ 4 คน ถ้าเยอะรอย่างนานไป อาจต้องเพิ่มเตา"
    sentiment, confidence = analyze_sentiment(text)
    print(f"ข้อความ: {text}")
    print(f"Sentiment: {sentiment}, Confidence: {confidence:.3f}")