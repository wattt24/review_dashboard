from sqlalchemy.orm import Session
from models.shopee_token import ShopeeToken
from datetime import datetime, timedelta

def save_token_to_db(db: Session, shop_id: str, access_token: str, refresh_token: str, expire_in: int):
    expire_at = datetime.utcnow() + timedelta(seconds=expire_in)

    token = db.query(ShopeeToken).filter_by(shop_id=shop_id).first()
    if token:
        token.access_token = access_token
        token.refresh_token = refresh_token
        token.expire_at = expire_at
    else:
        token = ShopeeToken(
            shop_id=shop_id,
            access_token=access_token,
            refresh_token=refresh_token,
            expire_at=expire_at
        )
        db.add(token)
    
    db.commit()
