# from database.all_database import 
import pandas as pd
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import pymysql,re,json
from textblob import TextBlob
from dateutil.relativedelta import relativedelta
from pythainlp.tokenize import word_tokenize
from pythainlp.corpus.common import thai_stopwords

# Initialize Thai sentiment analyzer
stopwords = set(thai_stopwords())
def get_connection():
    return pymysql.connect(
        host="yamanote.proxy.rlwy.net",
        user="root",
        password="yeiIByLVJqRlPrzKLGaNCNySevvHeabG",
        port=49296,
        database="railway",
        charset="utf8mb4"
    )
def clean_html(text):
    if text:
        return BeautifulSoup(text, "html.parser").get_text().replace("\n", " ").strip()
    return text
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


def extract_keywords(text):
    if text:
        tokens = [w for w in word_tokenize(text) if w.isalpha() and w not in stopwords]
        return json.dumps(tokens, ensure_ascii=False)  # ✅ แปลงเป็น JSON string
    return json.dumps([])
#โตกลางไว้รับทุกแพลตฟอร์ม รับเข้า
def save_reviews_to_db(reviews: list, platform: str, shop_id: str):
    """
    ฟังก์ชันกลาง: วิเคราะห์ + บันทึกรีวิวจากทุกแพลตฟอร์มลงฐานข้อมูล
    
    reviews: List ของ dict ที่มี key:
        - id (review_id)
        - review (ข้อความรีวิว)
        - date_created
        - rating (optional)
        - product_id (optional)
    
    platform: ชื่อแพลตฟอร์ม เช่น 'shopee', 'wordpress', 'facebook'
    shop_id: รหัสร้านที่สอดคล้องกัน
    """
    if not reviews:
        print("⚠️ ไม่มีรีวิวที่จะบันทึก")
        return

    conn = get_connection()
    cursor = conn.cursor()

    for r in reviews:
        review_id = str(r.get("id")).strip()
        raw_text = r.get("review", "")
        review_text = clean_html(raw_text)
        review_date = r.get("date_created")
        rating = r.get("rating")
        product_id = r.get("product_id")

        # วิเคราะห์
        sentiment = analyze_sentiment(review_text)
        keywords = extract_keywords(review_text)

        # บันทึก
        sql = """
        INSERT INTO reviews_history 
        (platform, shop_id, product_id, review_id, rating, review_text, sentiment, keywords, review_date, recorded_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
        ON DUPLICATE KEY UPDATE 
            rating = VALUES(rating),
            review_text = VALUES(review_text),
            sentiment = VALUES(sentiment),
            keywords = VALUES(keywords),
            review_date = VALUES(review_date)
        """

        cursor.execute(sql, (
            platform,
            shop_id,
            product_id,
            review_id,
            rating,
            review_text,
            sentiment,
            json.dumps(keywords, ensure_ascii=False) if isinstance(keywords, (dict, list)) else keywords,
            review_date
        ))

    conn.commit()
    cursor.close()
    conn.close()

    print(f"✅ บันทึกรีวิว {len(reviews)} รายการจากแพลตฟอร์ม '{platform}' แล้ว")

# ส่งข้อมูลจาก database จะ print ดู หรือ แสดงหน้าบนจอได้  ดึงreviews_historyข้อมูลทั้งหมด
def get_all_reviews(platform=None, shop_id=None, limit=100):
    conn = get_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    sql = "SELECT * FROM reviews_history"
    params = []

    if platform or shop_id:
        sql += " WHERE "
        conditions = []
        if platform:
            conditions.append("platform = %s")
            params.append(platform)
        if shop_id:
            conditions.append("shop_id = %s")
            params.append(shop_id)
        sql += " AND ".join(conditions)

    sql += " ORDER BY review_date DESC LIMIT %s"
    params.append(limit)

    cursor.execute(sql, params)
    results = cursor.fetchall()
    cursor.close()
    conn.close()

    # แปลงเป็น DataFrame เพื่อดูง่าย
    df = pd.DataFrame(results)# แปลงผลลัพธ์จาก MySQL (list ของ dict) → DataFrame
    print(f"✅ พบรีวิว {len(df)} รายการ")
    return df

def get_reviews_by_period(platform=None, shop_id=None, months=1):
    from database.all_database import get_connection
    import pymysql, pandas as pd

    conn = get_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    # ใช้ relativedelta ลบจำนวนเดือนจริง ๆ
    start_date = datetime.now() - relativedelta(months=months)

    sql = "SELECT * FROM reviews_history WHERE review_date >= %s"
    params = [start_date]

    if platform:
        sql += " AND platform = %s"
        params.append(platform)
    if shop_id:
        sql += " AND shop_id = %s"
        params.append(shop_id)

    sql += " ORDER BY review_date DESC"

    cursor.execute(sql, params)
    results = cursor.fetchall()
    cursor.close()
    conn.close()

    df = pd.DataFrame(results)
    return df