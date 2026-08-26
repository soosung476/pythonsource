from playwright.sync_api import sync_playwright
from pathlib import Path

BASE_DRI = Path(__file__).resolve().parent
Py_Scrap = BASE_DRI.parent/"Py_Scrap"

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()

    page.goto('http://google.com')
    page.screenshot(path=Py_Scrap/"img/Web1.png")

    page.goto('http://daum.net')
    page.screenshot(path=Py_Scrap/"img/Web2.png")

    browser.close()

print("스크린샷 성공")