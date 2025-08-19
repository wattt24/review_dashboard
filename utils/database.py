#utils/database.py
from sqlalchemy import create_engine

engine = create_engine("sqlite:///review_dashboard.db", echo=True, future=True)
