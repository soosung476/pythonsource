from playwright.sync_api import sync_playwright
from datetime import datetime
from pathlib import Path
import json
import time
import os
from dotenv import load_dotenv

load_dotenv()
id = os.getenv("wishket_id")
password = os.getenv("wishket_pwd")

BASE_DIR = Path(__file__).resolve().parent
Py_Scrap= BASE_DIR.parent/"Py_Scrap"


def crawl_wishket():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width":1920, "height":1080})

        page.goto('http://auth.wishket.com/login')
        page.wait_for_timeout(3000)

        page.fill(f'input[name="emailOrId"]', id)
        page.fill(f'input[name="password"]', password)

        login_button_xpath = '/html/body/div[2]/div[2]/div/div[2]/div/div[1]/form/div[3]/button'
        page.click(f'xpath = {login_button_xpath}')

        page.wait_for_timeout(3000)

        page.goto('https://www.wishket.com/project/')
        page.wait_for_timeout(3000)

        project_name=page.inner_text( 'xpath=//*[@id="projectListView"]/div/div[1]/div/section[1]/a/p')
        period = page.inner_text('xpath=//*[@id="projectListView"]/div/div[1]/div/section[1]/div[2]/p[2]/span')
        payment = page.inner_text('xpath=//*[@id="projectListView"]/div/div[1]/div/section[1]/div[2]/p[1]/span')
        payment = payment.replace(" /월", "")
        payment = payment.replace(",","")


        result = {
            "수집일시": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "프로젝트 명": project_name,
            "예상 기간": period,
            "금액": payment            
            
        }
        
        today = datetime.now().strftime("%Y%m%d")
        save_path = Py_Scrap/f"data/whishket_{today}.json"
        with open(save_path, "w", encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)


        csv_path = Py_Scrap/"data/whisket_history.csv"
        file_exists = os.path.isfile(csv_path)
        with open(csv_path, "a", encoding='utf-8-sig') as f:
            if not file_exists:
                f.write("수집일시, 프로젝트명, 기간, 금액\n")
            f.write(f'{result["수집일시"]},{project_name},{period},{payment}\n')


        print(f"저장 완료:{save_path}")
        return result

if __name__ == "__main__":
    crawl_wishket()

