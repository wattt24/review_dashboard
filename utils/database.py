#utils/database.py
from sqlalchemy import create_engine

engine = create_engine("mysql+pymysql://user:651324@localhost/review_dashboard")