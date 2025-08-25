from services.test_auth import get_token, save_token

# ข้อมูลจาก callback
code = "4f66526c5075746e426d497366474843"
shop_id = 225727065

# แลก access_token
token_data = get_token(code, shop_id)
print("Token Response:", token_data)

# ถ้าได้ access_token ให้เซฟลง Google Sheets
if "access_token" in token_data:
    save_token(
        shop_id,
        token_data["access_token"],
        token_data["refresh_token"],
        token_data["expires_in"],
        token_data["refresh_expires_in"]
    )
    print("✅ Token saved to Google Sheet")
else:
    print("❌ Failed to get token")
