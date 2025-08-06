from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from .base import Base

class ShopeeToken(Base):
    __tablename__ = "shopee_tokens"

    id = Column(Integer, primary_key=True, index=True)
    shop_id = Column(String(50), unique=True, nullable=False)
    access_token = Column(String(255), nullable=False)
    refresh_token = Column(String(255), nullable=False)
    expire_in = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
