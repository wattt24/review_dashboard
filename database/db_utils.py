# db_utils.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from config import DATABASE_URL
# กรอกข้อมูลการเชื่อมต่อ MySQL ตรงนี้

MYSQL_HOST = "localhost" # หรือ IP ถ้าเป็น server
MYSQL_PORT = 3306
MYSQL_USER = "root"
MYSQL_PASSWORD = "651324"
MYSQL_DB = "review_dashboarde"

# สร้าง connection string
connection_string = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB }"
engine = create_engine(connection_string)

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
