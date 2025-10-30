# from database.all_database import 
import pandas as pd
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import pymysql,re,json
from dateutil.relativedelta import relativedelta
from pythainlp.tokenize import word_tokenize
from pythainlp.corpus.common import thai_stopwords
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import torch.nn.functional as F
# Initialize Thai sentiment analyzer
stopwords = set(thai_stopwords())
# def get_connection():
#     return pymysql.connect(
#         host="yamanote.proxy.rlwy.net",
#         user="root",
#         password="yeiIByLVJqRlPrzKLGaNCNySevvHeabG",
#         port=49296,
#         database="railway",
#         charset="utf8mb4"
#     )

def get_connection():
    return pymysql.connect(
        host="localhost",           # ✅ อยู่เครื่องเดียวกับโค้ด
        user="root",        # 🔑 ชื่อผู้ใช้จาก DirectAdmin
        password="651324",   # 🔐 รหัสผ่านจาก DirectAdmin
        database="reviews_insight", # 🗄️ ชื่อฐานข้อมูลที่สร้างไว้
        port=3306,                  # ⚙️ พอร์ต MySQL ปกติ
        charset="utf8mb4",          # รองรับภาษาไทย
        cursorclass=pymysql.cursors.DictCursor
    )
def clean_html(text):
    if text:
        return BeautifulSoup(text, "html.parser").get_text().replace("\n", " ").strip()
    return text


# โหลดโมเดลและ tokenizer (ทำครั้งเดียวตอนเริ่มระบบ)
model_name = "FlukeTJ/distilbert-base-thai-sentiment"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)

# def analyze_For_sentiment(text: str):
#     # ✅ ป้องกัน None หรือไม่ใช่ string
#     if not text or not isinstance(text, str):
#         print("⚠️ ข้ามการวิเคราะห์ sentiment เพราะไม่มีข้อความรีวิว")
#         return 'neutral'

#     # ✅ ตัดข้อความเกิน 512 token อัตโนมัติ
#     inputs = tokenizer(
#         text,
#         return_tensors="pt",
#         truncation=True,   # ตัดส่วนเกินออก
#         max_length=512,    # จำกัดความยาวสูงสุด
#         padding=False
#     )
#     if "token_type_ids" in inputs:
#         del inputs["token_type_ids"]

#     with torch.no_grad():
#         outputs = model(**inputs)
#         probs = F.softmax(outputs.logits, dim=-1)
#         labels = ["negative", "neutral", "positive"]
#         idx = torch.argmax(probs, dim=-1).item()

#     return labels[idx]

NEGATIVE_KEYWORDS = ["แตก", "เสีย", "ห่วย", "พัง", "แย่", "คืนเงิน", "ช้า", "ไม่ดี", "เสียเวลา"]

def analyze_For_sentiment(text: str):
    if not text or not isinstance(text, str):
        return 'neutral'

    # ตรวจคำลบก่อน
    if any(word in text for word in NEGATIVE_KEYWORDS):
        rule_based = 'negative'
    else:
        rule_based = None

    # ใช้โมเดล
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
    if "token_type_ids" in inputs:
        del inputs["token_type_ids"]

    with torch.no_grad():
        outputs = model(**inputs)
        probs = F.softmax(outputs.logits, dim=-1)
        labels = ["negative", "neutral", "positive"]
        idx = torch.argmax(probs, dim=-1).item()
        model_sentiment = labels[idx]

    # ถ้ากฎเจอคำลบ → ใช้ rule-based
    if rule_based:
        return rule_based
    return model_sentiment

def extract_keywords(text):
    if text:
        tokens = [w for w in word_tokenize(text) if w.isalpha() and w not in stopwords]
        return json.dumps(tokens, ensure_ascii=False)  # ✅ แปลงเป็น JSON string
    return json.dumps([])

#โตกลางไว้รับทุกแพลตฟอร์ม รับเข้า
# def save_reviews_to_db(reviews: list, platform: str, shop_id: str):
#     """
#     ฟังก์ชันกลาง: วิเคราะห์ + บันทึกรีวิวจากทุกแพลตฟอร์มลงฐานข้อมูล
    
#     reviews: List ของ dict ที่มี key:
#         - id (review_id)
#         - review (ข้อความรีวิว)
#         - date_created
#         - rating (optional)
#         - product_id (optional)
    
#     platform: ชื่อแพลตฟอร์ม เช่น 'shopee', 'wordpress', 'facebook'
#     shop_id: รหัสร้านที่สอดคล้องกัน
#     """
#     if not reviews:
#         print("⚠️ ไม่มีรีวิวที่จะบันทึก")
#         return

#     conn = get_connection()
#     cursor = conn.cursor()

#     for r in reviews:
#         review_id = str(r.get("id")).strip()
#         raw_text = r.get("review", "")
#         review_text = clean_html(raw_text)
#         review_date = r.get("date_created")
#         rating = r.get("rating")
#         product_id = r.get("product_id")

#         # วิเคราะห์
#         sentiment = analyze_For_sentiment(review_text)
#         keywords = extract_keywords(review_text)

#         # บันทึก
#         sql = """
#         INSERT INTO reviews_history 
#         (platform, shop_id, product_id, review_id, rating, review_text, sentiment, keywords, review_date, recorded_at)
#         VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
#         ON DUPLICATE KEY UPDATE 
#             rating = VALUES(rating),
#             review_text = VALUES(review_text),
#             sentiment = VALUES(sentiment),
#             keywords = VALUES(keywords),
#             review_date = VALUES(review_date)
#         """

#         cursor.execute(sql, (
#             platform,
#             shop_id,
#             product_id,
#             review_id,
#             rating,
#             review_text,
#             sentiment,
#             json.dumps(keywords, ensure_ascii=False) if isinstance(keywords, (dict, list)) else keywords,
#             review_date
#         ))

#     conn.commit()
#     cursor.close()
#     conn.close()

#     print(f"✅ บันทึกรีวิว {len(reviews)} รายการจากแพลตฟอร์ม '{platform}' แล้ว")
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

        # ✅ ถ้าไม่มีข้อความรีวิว → ใช้ rating ตัดสิน sentiment
        if not review_text:
            if rating in [1, 2]:
                sentiment = "negative"
            elif rating == 3:
                sentiment = "neutral"
            elif rating in [4, 5]:
                sentiment = "positive"
            else:
                sentiment = "neutral"  # เผื่อกรณี rating ไม่มีหรือไม่ตรงเงื่อนไข
            keywords = json.dumps([])  # ไม่มีข้อความให้ดึง keyword
        else:
            # วิเคราะห์ sentiment ด้วยโมเดล
            sentiment = analyze_For_sentiment(review_text)
            keywords = extract_keywords(review_text)

        # ✅ บันทึกลงฐานข้อมูล
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
def get_all_reviews(platform=None, shop_id=None, limit=None):
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

    sql += " ORDER BY review_date DESC"

    if limit:
        sql += " LIMIT %s"
        params.append(limit)

    cursor.execute(sql, params)
    results = cursor.fetchall()
    cursor.close()
    conn.close()

    df = pd.DataFrame(results)
    print(f"✅ พบรีวิว {len(df)} รายการ")
    return df


# def get_reviews_by_period(platform=None, shop_id=None, months=1):
#     from database.all_database import get_connection
#     import pymysql, pandas as pd

#     conn = get_connection()
#     cursor = conn.cursor(pymysql.cursors.DictCursor)

#     # ใช้ relativedelta ลบจำนวนเดือนจริง ๆ
#     start_date = datetime.now() - relativedelta(months=months)

#     sql = "SELECT * FROM reviews_history WHERE review_date >= %s"
#     params = [start_date]

#     if platform:
#         sql += " AND platform = %s"
#         params.append(platform)
#     if shop_id:
#         sql += " AND shop_id = %s"
#         params.append(shop_id)

#     sql += " ORDER BY review_date DESC"

#     cursor.execute(sql, params)
#     results = cursor.fetchall()
#     cursor.close()
#     conn.close()

#     df = pd.DataFrame(results)
#     return df

def get_reviews_by_period(platform=None, shop_id=None, months=None):


    conn = get_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    params = []

    if months is not None:
        # ดึงเฉพาะช่วงเดือน
        start_date = datetime.now() - relativedelta(months=int(months))
        sql = "SELECT * FROM reviews_history WHERE review_date >= %s"
        params.append(start_date)
        if platform:
            sql += " AND platform = %s"
            params.append(platform)
        if shop_id:
            sql += " AND shop_id = %s"
            params.append(shop_id)
    else:
        # ดึงทั้งหมด
        sql = "SELECT * FROM reviews_history"
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

    sql += " ORDER BY review_date DESC"

    cursor.execute(sql, params)
    results = cursor.fetchall()
    cursor.close()
    conn.close()

    return pd.DataFrame(results)
