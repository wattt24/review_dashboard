# import sys
# import os

# # เพิ่ม root project folder เข้า sys.path ก่อน import modules
# project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
# if project_root not in sys.path:
#     sys.path.insert(0, project_root)

# import schedule
# import time
# from scraping.shopee_scraper import scrape_shopee
# from scraping.lazada_scraper import scrape_lazada
# from scraping.facebook_scraper import scrape_facebook
# from scraping.fujikaservice_scraper import scrape_fujikaservice
# from scraping.fujikathailand_scraper import scrape_fujikathailand
# from scraping.cps_oem_scraper import scrape_cps_oem
# from scraping.line_oa_scraper import scrape_line_oa

# def run_scheduler():
#     schedule.every().day.at("02:00").do(scrape_shopee)
#     print("✅ Scheduler started... Scraping will run daily at 02:00")
#     schedule.every().day.at("03:00").do(scrape_facebook)
#     schedule.every().day.at("04:00").do(scrape_lazada)
#     schedule.every().day.at("05:00").do(scrape_fujikaservice)
#     schedule.every().day.at("06:00").do(scrape_fujikathailand)
#     schedule.every().day.at("07:00").do(scrape_cps_oem)
#     schedule.every().day.at("08:00").do(scrape_line_oa)

#     while True:
#         schedule.run_pending()
#         time.sleep(60)
# if __name__ == "__main__":
#      run_scheduler()

import sys
import os

# เพิ่ม root project folder เข้า sys.path ก่อน import modules
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import schedule
import time
from shopee_api import scrape_shopee
from lazada_api import scrape_lazada
from scraping.facebook_scraper import scrape_facebook
from scraping.fujikaservice_scraper import scrape_fujikaservice
from scraping.fujikathailand_scraper import scrape_fujikathailand
from scraping.cps_oem_scraper import scrape_cps_oem
from scraping.line_oa_scraper import scrape_line_oa

def run_scheduler():
    print("✅ Scheduler started... รันทุก 10 วินาที")

    def job_and_save(scrape_func, filename):
        print(f"📥 เริ่มงาน {scrape_func.__name__} ...")
        data = scrape_func()
        import json
        os.makedirs('data', exist_ok=True)  # สร้างโฟลเดอร์ data ถ้าไม่มี
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"💾 บันทึกข้อมูลลง {filename} เรียบร้อย")

    schedule.every(10).seconds.do(job_and_save, scrape_shopee, 'data/shopee_mock.json')
    schedule.every(10).seconds.do(job_and_save, scrape_lazada, 'data/lazada_mock.json')
    schedule.every(10).seconds.do(job_and_save, scrape_facebook, 'data/facebook_mock.json')
    schedule.every(10).seconds.do(job_and_save, scrape_fujikaservice, 'data/fujikaservice_mock.json')
    schedule.every(10).seconds.do(job_and_save, scrape_fujikathailand, 'data/fujikathailand_mock.json')
    schedule.every(10).seconds.do(job_and_save, scrape_cps_oem, 'data/cps_oem_mock.json')
    schedule.every(10).seconds.do(job_and_save, scrape_line_oa, 'data/line_oa_mock.json')

    while True:
        schedule.run_pending()
        time.sleep(10)

if __name__ == "__main__":
    print("Starting update_jobs.py ...")
    run_scheduler()
