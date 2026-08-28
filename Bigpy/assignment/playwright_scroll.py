from pathlib import Path
from bs4 import BeautifulSoup
from  playwright.sync_api import sync_playwright
import requests


BASE_DIR = Path(__file__).resolve().parent

with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=False,
        args=[
            "--no-sandbox", # 리눅스 권한 문제 방지
            "--disable-dev-shm-usage", # 공유메모리 부족 방지
            "--disable-gpu", # GPU 비활성화
        ])

    page = browser.new_page(viewport={"width":1920, "height":1280})
    page.goto('https://store.ohou.se/today_deals')
    page.wait_for_timeout(4000)

    page.keyboard.press("PageDown")
    page.wait_for_timeout(1000)

    scroll_pause_time = 3000
    last_height = page.evaluate("document.documentElement.scrollHeight")

    while True:
        page.evaluate("window.scrollTo(0, document.documentElement.scrollHeight)")
        page.wait_for_timeout(scroll_pause_time)
        new_height = page.evaluate("document.documentElement.scrollHeight")
        if last_height == new_height:
                        break
        last_height = new_height
    html_content = page.content()
    browser.close()

soup = BeautifulSoup(html_content, 'html.parser')
# 현재 오늘의 집 스크롤 - div.css-a8wydj> div[data-element="Container"]섹션이 두개가 있음
# 하나는 div[data-element="Container"] > div[data-element="Grid"] > article.css-fgvjgs eb6kep22 
# 하나는 또다른 div[data-element="Container"] > 
# div[data-element="FeedSection"] 
# div[data-test-id="virtuoso-item-list"] div.css-n9q8wg e1qabbed0 <<

# top_sector, bot_sector로 나누자
# top_sector 셀렉터는 div[data-element="Container"] > div[data-element="Grid"] > article.css-fgvjgs
# top의 이미지는 top_sector.select 를 img.thumbnail-image e1bro5mc1 css-7bfh27 이용하여 리스트로 담을 수 있음
# top의 title은 div.css-vwmz5u e1dpojfn8
# top의 price는 p[data-element="DisplayPrice"]

# bot_sector 셀렉터는 div[data-element="Container"] > div[data-element="FeedSection"] div[data-test-id="virtuoso-item-list"] article.eic8x3q0
# bot의 이미지는 bot_sector.select 를 img.thumbnail-image
# bot의 title은 span.product-name 안에 text로 존재
# bot의 price는 기본가격으로 가져올 예정, span.css-o8ych2 안에 있음.

ins_cnt = 2 # 엑셀까지 확장할 시 두번째 행부터 저장하기 위해서 일단 선언.

top_sector = soup.select('div.css-a8wydj> div[data-element="Container"]')[0]
bot_sector = soup.select('div.css-a8wydj> div[data-element="Container"]')[1]
# print(top_sector)
# print("="*100)
# print(bot_sector)

# 프린트 결과 잘 가져와 졌음.

top_img = top_sector.select("img.thumbnail-image")
top_title_list = top_sector.select("div.css-vwmz5u")
top_title = [d.contents[-1].strip() for d in top_title_list] # 클로드 도움
top_price = top_sector.select("p[data-element='DisplayPrice']")

bot_img = bot_sector.select("img.thumbnail-image")
bot_title_list = bot_sector.select("span.product-name")
bot_title = [s.get_text(strip=True) for s in bot_title_list]
bot_price = bot_sector.select("span.css-o8ych2")


# 이미지, 프라이스는 나중에 심화 과정으로 엑셀에 저장.

with open(BASE_DIR / "titles.txt", "w", encoding="utf-8") as f:
    for title in top_title:
        f.write(title + "\n")
    for title in bot_title:
        f.write(title+"\n")
        
# title 저장까지 검증 완료. 이미지, 프라이스를 엑셀에 저장하는건 주말에 추가.