# create_tables.py

from models.shopee_token import Base
from database.session import engine

# สร้างตารางทั้งหมดตาม models
print("⏳ Creating database tables...")
Base.metadata.create_all(bind=engine)
print("✅ Tables created successfully.")

