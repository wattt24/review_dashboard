# เอา short-lived token ที่ได้มาจาก Graph API Explorer แปลงเป็น long-lived และบันทึกลง Google Sheet
# https://graph.facebook.com/v17.0/oauth/access_token?grant_type=fb_exchange_token&client_id=2233454897103615&client_secret=f7dcecc20c8292cac3836d475cf82832&fb_exchange_token=EAAfvUL3Dgv8BPg4hIk9eYA3eOHFWZCq6TcRvm93k70RrPZCCeu2zUl2ccCwosJ18mQr6avsJTNbZBVZBbS72PqEIxMrZCjCJScVTZBTHDAKyZAgkZBYc8k9ZBTcZBZBWT5k5djIADqw2HJS3g1oSOe6esdE50QcakXRk22yuHefaYlhrK8gvkVllJNRju1DlDYe4DfwayENs3V5cgbOASlZBGUmnl98is2XQZBGBjjEksL8zcos55ZBQZDZD
from datetime import datetime, timedelta
# respones จาก url ด้านบน
# {"access_token":"EAAfvUL3Dgv8BPr3ZAEscIuKwz37QZABZBDbIyFyWSZAABYcZAosevZBDyZB0tflgWUq7iQyAPtI6kJUvDwrJ7mUcTMJyhRQUDgoQKSEaSdHl6ZA4HM8CLZAgsm75wNrpCsLqi9K0ZCeOQc09Tj5mSd1phoBZBUo1cOqMt7R0tsvhSeLY509dFKmoNQLaPO63MUTpD8m","token_type":"bearer"}
long_lived_token = ""

# สมมติ 60 วัน คำนวณเวลาเองเนื่องจาก ไม่มี expires_in ไม่ระบุอายุจึงคำนวณ expired_at จากเวลาปัจจุบัน
expires_in = 60 * 24 * 3600

now = datetime.now()
expired_at = now + timedelta(seconds=expires_in)

print("Token หมดอายุ:", expired_at.isoformat())
