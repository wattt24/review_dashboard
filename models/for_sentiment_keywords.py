import re
from collections import Counter
from textblob import TextBlob

# -------------------------
# 1️⃣ Clean HTML / text
# -------------------------
def clean_html(text):
    """
    ลบ HTML tag, whitespace เกิน, newline, special characters
    """
    if not isinstance(text, str):
        return ""
    # ลบ tag HTML
    clean = re.sub(r"<.*?>", "", text)
    # ลบ whitespace เกิน
    clean = re.sub(r"\s+", " ", clean)
    # ลบตัวอักษรพิเศษ (ยกเว้น . , ! ?)
    clean = re.sub(r"[^\w\s\.,!?]", "", clean)
    return clean.strip()

# -------------------------
# 2️⃣ Extract Keywords (โดยไม่ต้องกำหนด stopwords)
# -------------------------
def extract_keywords(text, top_n=5):
    """
    ดึงคำสำคัญจาก text โดยนับความถี่ของคำ
    ไม่ต้องตั้ง stopwords
    """
    if not isinstance(text, str) or not text:
        return []
    # clean text
    text = clean_html(text).lower()
    # split words
    words = re.findall(r"\b\w+\b", text)
    # นับความถี่
    count = Counter(words)
    # คืนค่า top_n
    return [word for word, freq in count.most_common(top_n)]

# -------------------------
# 3️⃣ Analyze Sentiment
# -------------------------
def analyze_sentiment(text):
    """
    วิเคราะห์ความรู้สึก (บวก / ลบ / กลาง) ด้วย TextBlob
    """
    if not isinstance(text, str) or not text:
        return "neutral"
    
    blob = TextBlob(clean_html(text))
    polarity = blob.sentiment.polarity  # -1 ถึง 1
    if polarity > 0.1:
        return "positive"
    elif polarity < -0.1:
        return "negative"
    else:
        return "neutral"