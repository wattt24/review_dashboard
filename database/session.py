from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# ตัวอย่าง SQLite
# DATABASE_URL = "sqlite:///./review_dashboard.db"

# หรือ MySQL (ใช้ของคุณแทน)
DATABASE_URL = "mysql+pymysql://username:password@localhost:3306/review_dashboard"

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
