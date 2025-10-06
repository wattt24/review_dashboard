from bs4 import BeautifulSoup
import pandas as pd
import mysql.connector
from database.all_database import get_connection
from textblob import TextBlob
from pythainlp.tokenize import word_tokenize
from pythainlp.corpus.common import thai_stopwords

# Initialize Thai sentiment analyzer
stopwords = set(thai_stopwords())


def analyze_sentiment(text):
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    if polarity > 0.05:
        return 'positive'
    elif polarity < -0.05:
        return 'negative'
    else:
        return 'neutral'
# --- ฟังก์ชันช่วยเหลือ ---
def clean_html(text):
    if text:
        return BeautifulSoup(text, "html.parser").get_text().replace("\n", " ").strip()
    return text

def extract_keywords(text):
    if text:
        tokens = [w for w in word_tokenize(text) if w.isalpha() and w not in stopwords]
        return ','.join(tokens)
    return None



# --- ดึงรีวิวจาก platform ใดก็ได้ ---
def get_reviews(platform: str):
    conn = get_connection()
    df = pd.read_sql("SELECT review_id, review_text, sentiment, keywords FROM reviews_history WHERE platform = %s AND (sentiment IS NULL OR keywords IS NULL)", conn, params=[platform])

    conn.close()

    # ทำความสะอาด HTML
    df['review_text'] = df['review_text'].apply(clean_html)
    return df

# --- อัปเดต sentiment + keywords ลง MySQL ---
def update_sentiment_keywords(df: pd.DataFrame):
    if df.empty:
        print("ไม่มีรีวิวที่ต้องประมวลผล")
        return

    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="yourpassword",
        database="review_dashboard"
    )
    cursor = conn.cursor()

    for _, row in df.iterrows():
        rid = row['review_id']
        text = row['review_text']

        sentiment = analyze_sentiment(text)
        keywords = extract_keywords(text)

        cursor.execute("""
            UPDATE reviews_history
            SET sentiment = %s, keywords = %s
            WHERE review_id = %s
        """, (sentiment, keywords, rid))

    conn.commit()
    cursor.close()
    conn.close()
    print(f"✅ อัปเดต sentiment + keywords {len(df)} รีวิวเรียบร้อย")