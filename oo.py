# # -*- coding: utf-8 -*-
# from pythainlp.tokenize import word_tokenize

# # ตัวอย่าง Lexicon แบบง่าย
# POSITIVE_WORDS = ["ดี", "เยี่ยม", "สวย", "ชอบ", "ถูกใจ", "รัก", "ยอดเยี่ยม"]
# NEGATIVE_WORDS = ["แย่", "ไม่ดี", "ช้า", "เสียใจ", "ผิดหวัง", "เบื่อ", "ไม่พอใจ"]

# def analyze_sentiment(text):
#     """
#     วิเคราะห์ sentiment ภาษาไทยแบบง่าย
#     คืนค่า: 'positive', 'negative', 'neutral'
#     """
#     if not text or not isinstance(text, str):
#         return 'neutral'

#     tokens = word_tokenize(text)
#     pos_count = sum(1 for t in tokens if t in POSITIVE_WORDS)
#     neg_count = sum(1 for t in tokens if t in NEGATIVE_WORDS)

#     if pos_count > neg_count:
#         return 'positive'
#     elif neg_count > pos_count:
#         return 'negative'
#     else:
#         return 'neutral'

# # ---------------------------
# # ทดสอบโค้ด
# # ---------------------------
# if __name__ == "__main__":
#     test_texts = [
#         "สินค้านี้ดีมาก คุณภาพเยี่ยม",
#         "ช้าและบริการไม่ประทับใจ",
#         "ปกติค่ะ ไม่มีอะไรพิเศษ",
#         "",
#         None
#     ]

#     for text in test_texts:
#         result = analyze_sentiment(text)
#         print(f"ข้อความ: {text}\nSentiment: {result}\n")
from bs4 import BeautifulSoup
import pandas as pd

# 🧹 ฟังก์ชันล้าง HTML ออกจากข้อความ
def clean_html(text):
    """ล้างแท็ก HTML ออกจากข้อความ เหลือเฉพาะข้อความล้วน"""
    if text:
        return BeautifulSoup(text, "html.parser").get_text().replace("\n", " ").strip()
    return text

data = {
    "review_id": [10391984933, 10391994936, 10396240713],
    "review": [
        # ✅ รีวิวที่ 1 (ข้อความจริง)
        "<p>ได้รับสินค้าครบตามที่สั่ง <b>โอริง</b> ที่สั่งมาใส่ได้ตรงตามจุด "
        "สั่งตามรูปแบบที่ร้านทำตำแหน่งไว้ให้ เข้าใจง่าย ร้านจัดส่งไว "
        "ขนส่งก็ดี</p>",

        # ✅ รีวิวที่ 2 (ข้อความจริงแบบมี tag)
        "<ul><li>ปิดผนึกวาล์วได้อย่างมีประสิทธิภาพ</li>"
        "<li>ปะเก็นยางที่ทนทาน</li>"
        "<li>เหมาะกับปั๊มหลายรุ่น</li>"
        "<li>อะไหล่ทดแทนที่เชื่อถือได้</li>"
        "<li>แหวนยางกันรั่ว</li>"
        "<li>รับประกันการไหลของน้ำที่ราบรื่น</li></ul>",

        # รีวิวที่ 3 (เหมือนเดิม)
        "<p>กล่องบุบ แต่ของใช้ได้ดี</p>"
    ]
}

# 🔧 สร้าง DataFrame จำลอง
df = pd.DataFrame(data)

# 🧠 ใช้ฟังก์ชัน clean_html กับคอลัมน์ review
df["clean_review"] = df["review"].apply(clean_html)

# 🎨 แสดงผลลัพธ์แบบอ่านง่าย
print("="*60)
print("🧾 ตัวอย่างก่อนและหลังการล้าง HTML ด้วย clean_html()")
print("="*60)

for _, row in df.iterrows():
    print("platform: shopee")
    print(f"รีวิว ID: {row['review_id']} ")
    print(f"review: {row['review']} ")
    print(f"clean review : {row['clean_review']}")
    print("-"*60)
