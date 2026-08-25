from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

url = "https://www.dhlottery.co.kr/lt645/result?round=1150"

driver = webdriver.Chrome()
driver.get(url)

wait = WebDriverWait(driver, 15)

# 1. 활성화된 슬라이드 안의 result-date에 텍스트가 채워질 때까지 대기
desc_locator = (By.CSS_SELECTOR, "div.swiper-slide-active div.result-date")
wait.until(lambda d: d.find_element(*desc_locator).text.strip() != "")
desc = driver.find_element(*desc_locator)
print("추첨일:", desc.text.strip())

# 2. 활성화된 슬라이드 안에서 공 번호 가져오기
ball_box = driver.find_element(By.CSS_SELECTOR, "div.swiper-slide-active div.result-ballBox")
balls = ball_box.find_elements(By.CSS_SELECTOR, "div.result-ball")

# 텍스트 채워질 때까지 대기 (첫 번째 공 기준)
wait.until(lambda d: balls[0].text.strip() != "")

win_numbers = [b.text.strip() for b in balls[:6]]
bonus_number = balls[6].text.strip() if len(balls) >= 7 else "정보 없음"

print("당첨번호:", win_numbers)
print("보너스번호:", bonus_number)

driver.quit()