
import pandas as pd
import pymysql
def get_connection():
    return pymysql.connect(
        host="yamanote.proxy.rlwy.net",
        user="root",
        password="yeiIByLVJqRlPrzKLGaNCNySevvHeabG",
        port=49296,
        database="railway",
        charset="utf8mb4"
    )
def load_reviews(months=None):
    conn = get_connection()
    query = """
        SELECT platform, shop_id, product_id, review_id, rating, review_text, sentiment, keywords, review_date
        FROM reviews_history
        ORDER BY review_date DESC
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df