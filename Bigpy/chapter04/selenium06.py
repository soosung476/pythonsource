from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from pathlib import Path
import time
import os
from dotenv import load_dotenv

load_dotenv()
id = os.getenv("wishket_id")
password = os.getenv("wishket_pwd")

BASE_DIR = Path(__file__).resolve().parent
Py_Scrap= BASE_DIR.parent/"Py_Scrap"

chrome_options = Options()
s = Service(Py_Scrap/"chromedriver/chromedriver")
driver = webdriver.Chrome(service=s, options=chrome_options)

driver.set_window_size(1920,1080)
driver.get('http://auth.wishket.com/login')
time.sleep(3)

driver.find_element(By.NAME, 'emailOrId').send_keys(id)
driver.find_element(By.NAME, 'password').send_keys(password)

# 로그인 버튼
login_button_xpath = '/html/body/div[2]/div[2]/div/div[2]/div/div[1]/form/div[3]/button'
driver.find_element(By.XPATH, login_button_xpath).click()
driver.save_screenshot(Py_Scrap/"img/wishWeb.png")
time.sleep(3)
print("로그인 성공")

# 포트폴리오 페이지로 이동
driver.get('https://www.wishket.com/project/')
time.sleep(3)

# 프로젝트 정보 크롤링

project_name=driver.find_element(By.XPATH, '//*[@id="projectListView"]/div/div[1]/div/section[1]/a/p').text
period = driver.find_element(By.XPATH, '//*[@id="projectListView"]/div/div[1]/div/section[1]/div[2]/p[2]/span').text
payment = driver.find_element(By.XPATH, '//*[@id="projectListView"]/div/div[1]/div/section[1]/div[2]/p[1]/span').text
payment = payment.replace(" /월", "")

print(f"프로젝트 명: {project_name}")
print(f"예상 기간: {period}")
print(f"금액: {payment}")

driver.quit()

print("스크린샷 성공")