# database/models/oauth_token.py

from sqlalchemy import Column, Integer, String, BigInteger, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class OAuthToken(Base):
    __tablename__ = "oauth_tokens"

    id = Column(Integer, primary_key=True, index=True)
    platform = Column(String(50), nullable=False)
    shop_id = Column(BigInteger, nullable=False)
    access_token = Column(Text, nullable=False)
    refresh_token = Column(Text, nullable=False)
    expire_in = Column(Integer, nullable=False)
    obtained_at = Column(DateTime, default=datetime.utcnow)
