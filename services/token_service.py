from sqlalchemy.orm import Session
from datetime import datetime
from database import SessionLocal
from models import OAuthToken  # import model ที่จะสร้างในขั้นตอนถัดไป

def save_token_to_db(platform, shop_id, access_token, refresh_token, expire_in):
    db: Session = SessionLocal()

    # ลองเช็กก่อนว่ามี shop_id นี้ใน platform นี้ไหม
    existing = db.query(OAuthToken).filter_by(platform=platform, shop_id=shop_id).first()

    if existing:
        existing.access_token = access_token
        existing.refresh_token = refresh_token
        existing.expire_in = expire_in
        existing.obtained_at = datetime.utcnow()
    else:
        token = OAuthToken(
            platform=platform,
            shop_id=shop_id,
            access_token=access_token,
            refresh_token=refresh_token,
            expire_in=expire_in,
            obtained_at=datetime.utcnow()
        )
        db.add(token)

    db.commit()
    db.close()
