
from flask import Flask
import os
from services.test_auth import get_token, save_token

app = Flask(__name__)

@app.route("/exchange_token")
def exchange_token():
    CODE = os.environ.get("SHOPEE_CODE")
    SHOP_ID = int(os.environ.get("SHOPEE_SHOP_ID"))

    token_data = get_token(CODE, SHOP_ID)

    if "access_token" in token_data:
        save_token(
            SHOP_ID,
            token_data["access_token"],
            token_data["refresh_token"],
            token_data["expires_in"],
            token_data["refresh_expires_in"]
        )
        return "✅ Access token saved to Google Sheet"
    else:
        return f"❌ Failed to get token: {token_data}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
