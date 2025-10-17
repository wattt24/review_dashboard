# line_oa_processing.py
from transformers import pipeline
import pandas as pd
import psycopg2

import plotly.express as px
import streamlit as st
from database.all_database import get_connection
import pandas as pd
from database.all_database import get_connection

def inspect_line_messages(limit=10):
    conn = get_connection()
    query = f"SELECT * FROM line_messages ORDER BY created_at DESC LIMIT {limit};"
    df = pd.read_sql(query, conn)
    conn.close()

    print("🧱 คอลัมน์ทั้งหมดใน line_messages:")
    print(df.columns.tolist())
    print("\n📊 ตัวอย่างข้อมูล:")
    print(df.head())

    print(f"\nรวมทั้งหมด {len(df)} แถว")
    return df
def fetch_line_messages(limit=50):
    conn = get_connection()
    query = f"""
        SELECT id, user_id, message, created_at
        FROM line_messages
        WHERE message_type = 'text'
          AND direction = 'user'
          AND message IS NOT NULL
        ORDER BY created_at DESC
        LIMIT {limit};
    """
    df = pd.read_sql(query, conn)
    conn.close()
    print(f"✅ ดึงข้อมูลมาแล้ว {len(df)} ข้อความ")
    return df

def check_unique_values():
    conn = get_connection()
    df = pd.read_sql("SELECT message_type, direction, COUNT(*) FROM line_messages GROUP BY message_type, direction;", conn)
    conn.close()
    print(df)
    return df
# ==========================
# 2️⃣ โหลดโมเดลสำหรับจัดหมวดหมู่
# ==========================
def get_classifier():
    print("📦 กำลังโหลดโมเดล zero-shot classification...")
    return pipeline("zero-shot-classification", model="MoritzLaurer/mDeBERTa-v3-base-mnli-xnli")




# ==========================
# 3️⃣ ฟังก์ชันจัดประเภทข้อความ
# ==========================
def classify_message(text, classifier):
    labels = ["คำถาม", "รีวิวสินค้า", "คำชม", "ร้องเรียน", "สอบถามบริการ", "อื่นๆ"]
    try:
        result = classifier(text, candidate_labels=labels, multi_label=False)
        if result and "labels" in result and "scores" in result:
            return result["labels"][0], float(result["scores"][0])
        else:
            return "อื่นๆ", 0.0
    except Exception as e:
        print(f"⚠️ classify_message error: {e}")
        return "อื่นๆ", 0.0


# ==========================
# 4️⃣ วิเคราะห์ข้อความทั้งหมด
# ==========================
def analyze_messages(df):
    if df.empty:
        df["category"] = []
        df["confidence"] = []
        return df

    classifier = get_classifier()
    results = [classify_message(x, classifier) for x in df["message"]]
    df["category"], df["confidence"] = zip(*results)
    return df


def analyze_and_display_all():
    df = fetch_line_messages()
    if df.empty:
        print("❌ ไม่มีข้อความให้วิเคราะห์")
        return
    
    classifier = get_classifier()
    print("🔍 กำลังวิเคราะห์ข้อความ...")

    results = [classify_message(msg, classifier) for msg in df["message"]]
    df["category"], df["confidence"] = zip(*results)
    
    print("✅ วิเคราะห์เสร็จแล้ว")
    # แสดงผลทุกแถว
    pd.set_option("display.max_rows", None)  # แสดงทุกแถว
    pd.set_option("display.max_colwidth", None)  # แสดงข้อความเต็ม
    print(df[["message", "category", "confidence"]])

def summarize_categories(df):
    summary = df["category"].value_counts().reset_index()
    summary.columns = ["Category", "Count"]
    summary["Percent"] = (summary["Count"] / len(df) * 100).round(2)
    return summary

def summarize_confidence(df):
    summary = df.groupby("category")["confidence"].agg(
        ['count', 'mean', 'max']
    ).sort_values(by="mean", ascending=False).reset_index()
    summary.rename(columns={
        "count": "จำนวนข้อความ",
        "mean": "ความมั่นใจเฉลี่ย",
        "max": "ความมั่นใจสูงสุด"
    }, inplace=True)
    summary["ความมั่นใจเฉลี่ย"] = summary["ความมั่นใจเฉลี่ย"].round(3)
    summary["ความมั่นใจสูงสุด"] = summary["ความมั่นใจสูงสุด"].round(3)
    return summary
