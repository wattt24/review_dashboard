#Dockerfile
#หน้าที่ใช้ image Python 3.12 เป็นฐาน
FROM python:3.12-slim 

#หน้าที่ตั้งที่ทำงานหลักเป็น /app
WORKDIR /app

#หน้าที่คัดลอกไฟล์โปรเจกต์เข้า container
COPY . .

#หน้าที่ติดตั้ง dependencies จาก requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

#หน้าที่สั่งให้ container เริ่มรัน main.py เมื่อเปิด
CMD ["python", "main.py"]
