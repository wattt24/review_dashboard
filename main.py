from services.shopee_auth import get_token

code = "59487941577441765072796f4a616445"  # code ที่ได้จาก Shopee
shop_id = 225734279                          # shop_id ของร้านค้า

token_response = get_token(code, shop_id)
print(token_response)
งงงววว