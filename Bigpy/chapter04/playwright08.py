from playwright.sync_api import sync_playwright
from pathlib import Path

BASE_DRI = Path(__file__).resolve().parent
Py_Scrap = BASE_DRI.parent/"Py_Scrap"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False) # 기본값 headless = True, 따라서 웹페이지가 보이지 않고 screenshot 저장됨.
    page = browser.new_page(viewport={"width":1920, "height":1080})

    page.goto('http://google.com')
    page.wait_for_timeout(3000)
    page.screenshot(path=Py_Scrap/"img/Web3.png")

    page.goto('http://daum.net')
    page.wait_for_timeout(3000)
    page.screenshot(path=Py_Scrap/"img/Web4.png")

    browser.close()

print("스크린샷 성공")