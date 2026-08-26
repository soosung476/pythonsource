from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from pathlib import Path
import time

BASE_DIR = Path(__file__).resolve().parent
Py_Scrap= BASE_DIR.parent/"Py_Scrap"

chrome_options = Options()
s = Service(Py_Scrap/"chromedriver/chromedriver")

driver = webdriver.Chrome(service=s, options=chrome_options)

driver.set_window_size(1920,1080)

driver.get('http://google.com')
time.sleep(3) # 대기 (모든 load 시간 3초 기다림)
driver.save_screenshot(Py_Scrap/"img/Website3.png")

driver.set_window_size(1920,1080)
driver.get('http://daum.net')
time.sleep(3)
driver.save_screenshot(Py_Scrap/"img/Website4.png")

driver.quit()

print("스크린샷 성공")


