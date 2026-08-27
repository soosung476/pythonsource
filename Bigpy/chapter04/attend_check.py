from playwright.sync_api import sync_playwright
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
SESSION_FILE = BASE_DIR/"naver_session.json"

def attend_with_saved_session():
    if not os.path.isfile(SESSION_FILE):
        print("저장된 세션이 없습니다. save_session.py를 먼저 실행하세요.")
        return

    with sync_playwright() as p:
        browser = p.chromium.launch()  # 자동 실행용이니 headless 유지
        context = browser.new_context(storage_state=SESSION_FILE)
        page = context.new_page()

        page.goto('http://cafe.naver.com/paramsx?iframe_url=/AttendanceView.nhn%3Fsearch.clubid=19756449%26search.menuid=103')
        page.wait_for_timeout(3000)

        page.once("dialog", lambda dialog: dialog.accept())

        frame = page.frame(name="cafe_main")
        if frame:
            frame.fill('#cmtinput', '출석합니다')
            frame.click('#btn-submit-attendance')
            page.wait_for_timeout(3000)
            print("출석체크 완료")
        else:
            print("cafe_main iframe을 못 찾음 — 세션이 만료됐을 가능성. save_session.py 다시 실행 필요")
            page.screenshot(path="attend_fail.png")  # 실패 시 원인 파악용

        browser.close()


if __name__ == '__main__':
    attend_with_saved_session()