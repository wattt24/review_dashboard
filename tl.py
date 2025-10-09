import time, requests

for i in range(3):
    try:
        res = requests.get("https://example.com/api")
        res.raise_for_status()
        print("✅ Success")
        break
    except requests.exceptions.RequestException as e:
        print(f"Attempt {i+1} failed:", e)
        time.sleep(5)