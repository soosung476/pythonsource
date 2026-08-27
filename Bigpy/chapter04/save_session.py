from playwright.sync_api import sync_playwright
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent 

def save_login_session():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto('https://nid.naver.com/nidlogin.login')

        input(" 브라우저 창에서 아이디/ 비밀번호 직접 입력 후 로그인 -> 로그인 완료되면 엔터를 눌러주세요")

        page.context.storage_state(path= BASE_DIR/"naver_session.json")
        print("세션 저장 완료: naver_session.json")
        browser.close()


if __name__ == '__main__':
    save_login_session()