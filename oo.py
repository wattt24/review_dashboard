#test
from api.fujikathailand_rest_api import get_connection
import pandas as pd

conn = get_connection()
df = pd.read_sql("SELECT * FROM reviews_history LIMIT 10", conn)
conn.close()
print(df.head())