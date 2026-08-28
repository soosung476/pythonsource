"""
유튜브 영상의 댓글을 Playwright로 수집해서 엑셀로 저장한다.

- 무한 스크롤로 댓글을 계속 로딩시킨 뒤
- 작성자 / 댓글내용 / 좋아요 / 프로필이미지(실제 이미지) 를 뽑아서
- xlsxwriter 로 엑셀 파일에 기록한다.

사용법:
    python exampleyoutube.py                      # 기본 영상 URL 사용
    python exampleyoutube.py <영상URL>
    python exampleyoutube.py <영상URL> --max 50   # 최대 50개만
    python exampleyoutube.py <영상URL> --show     # 브라우저 창을 띄워서 확인
"""

import argparse
import sys
from io import BytesIO
from pathlib import Path

import requests
import xlsxwriter
from PIL import Image
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright

BASE_DIR = Path(__file__).resolve().parent
Py_Scrap = BASE_DIR.parent / "Py_Scrap"
SAVE_PATH = Py_Scrap / "data" / "youtube_comments.xlsx"

DEFAULT_URL = "https://www.youtube.com/watch?v=BBJa32lCaaY"

# 댓글 한 덩어리(스레드) 와 그 안의 항목들
THREAD = "ytd-comment-thread-renderer"
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
)

# 엑셀 셀 크기 (프로필 이미지를 넣을 자리)
IMG_BOX_PX = 44          # 이미지를 이 크기(px)에 맞춰 넣는다
ROW_HEIGHT_PT = 36       # 36pt == 48px
IMG_COL_WIDTH = 8        # 약 61px


# ---------------------------------------------------------------- 크롤링

def accept_consent(page):
    """유럽/일부 지역에서 뜨는 쿠키 동의창이 있으면 닫는다."""
    for selector in (
        'button[aria-label*="Accept"]',
        'button[aria-label*="모두 수락"]',
        'button[aria-label*="동의"]',
    ):
        try:
            button = page.locator(selector).first
            if button.is_visible(timeout=1000):
                button.click()
                page.wait_for_timeout(1000)
                return
        except PlaywrightTimeoutError:
            continue
        except Exception:
            continue


def scroll_comments(page, max_comments, max_rounds=60):
    """댓글이 더 이상 늘지 않을 때까지 아래로 스크롤한다."""
    # 댓글 영역은 조금 내려야 로딩이 시작된다.
    page.mouse.wheel(0, 1500)
    try:
        page.wait_for_selector(THREAD, timeout=15000)
    except PlaywrightTimeoutError:
        print("댓글을 찾지 못했습니다. (댓글 사용 중지 영상이거나 로딩 실패)")
        return 0

    loaded = page.locator(THREAD).count()
    stable = 0  # 개수가 그대로인 횟수

    for _ in range(max_rounds):
        if max_comments and loaded >= max_comments:
            break

        # 마지막 댓글을 화면 안으로 끌어오면 다음 묶음이 로딩된다.
        # (End 키는 영상 재생 위치를 옮겨버려서 쓰지 않는다.)
        try:
            page.locator(THREAD).last.scroll_into_view_if_needed(timeout=5000)
        except Exception:
            page.mouse.wheel(0, 3000)
        page.wait_for_timeout(1500)

        current = page.locator(THREAD).count()
        print(f"  ...로딩된 댓글 {current}개")

        if current == loaded:
            stable += 1
            if stable >= 3:  # 3번 연속 그대로면 끝까지 내려온 것
                break
        else:
            stable = 0
            loaded = current

    return page.locator(THREAD).count()


def extract_comments(page, max_comments):
    """DOM에서 작성자/내용/좋아요/프로필이미지 URL 을 한 번에 뽑아온다."""
    rows = page.eval_on_selector_all(
        THREAD,
        """(threads) => threads.map((t) => {
            const pick = (sel) => {
                const el = t.querySelector(sel);
                return el ? el.textContent.trim() : "";
            };
            const img = t.querySelector("#author-thumbnail img");
            return {
                author: pick("#author-text"),
                content: pick("#content-text"),
                likes: pick("#vote-count-middle"),
                profile: img ? (img.getAttribute("src") || "") : "",
            };
        })""",
    )

    comments = []
    for row in rows:
        # 내용이 비어 있으면 아직 렌더링 안 된 껍데기라 건너뛴다.
        if not row["content"]:
            continue
        row["likes"] = row["likes"] or "0"
        comments.append(row)
        if max_comments and len(comments) >= max_comments:
            break

    return comments


def crawl(url, max_comments, headless=True):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context(
            user_agent=USER_AGENT,
            locale="ko-KR",
            viewport={"width": 1280, "height": 900},
        )
        page = context.new_page()

        print(f"접속 : {url}")
        page.goto(url, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(3000)

        accept_consent(page)

        title = page.title().replace(" - YouTube", "")
        print(f"영상 : {title}")

        scroll_comments(page, max_comments)
        comments = extract_comments(page, max_comments)

        browser.close()

    return title, comments


# ---------------------------------------------------------------- 엑셀 저장

def fetch_thumbnail(session, url, cache):
    """프로필 이미지를 내려받아 엑셀이 읽을 수 있는 PNG 바이트로 바꾼다."""
    if not url or not url.startswith("http"):
        return None
    if url in cache:  # 같은 사람이 여러 번 댓글을 달았을 때 재사용
        return cache[url]

    try:
        res = session.get(url, timeout=5)
        res.raise_for_status()
        # webp 로 내려오는 경우가 있어서 PNG 로 변환해 둔다.
        image = Image.open(BytesIO(res.content)).convert("RGB")
        buffer = BytesIO()
        image.save(buffer, format="PNG")
        data = (buffer, image.width)
    except Exception as e:
        print(f"  프로필 이미지 실패 : {e}")
        data = None

    cache[url] = data
    return data


def save_excel(comments, save_path, video_title):
    save_path.parent.mkdir(parents=True, exist_ok=True)

    workbook = xlsxwriter.Workbook(save_path)
    worksheet = workbook.add_worksheet("comments")

    header = workbook.add_format(
        {"bold": True, "bg_color": "#FF0000", "font_color": "white",
         "align": "center", "valign": "vcenter", "border": 1}
    )
    cell = workbook.add_format({"valign": "vcenter", "border": 1})
    wrap = workbook.add_format(
        {"valign": "vcenter", "text_wrap": True, "border": 1}
    )
    center = workbook.add_format(
        {"valign": "vcenter", "align": "center", "border": 1}
    )

    worksheet.write("A1", "작성자", header)
    worksheet.write("B1", "댓글내용", header)
    worksheet.write("C1", "좋아요", header)
    worksheet.write("D1", "프로필이미지", header)

    worksheet.set_column("A:A", 20)
    worksheet.set_column("B:B", 70)
    worksheet.set_column("C:C", 10)
    worksheet.set_column("D:D", IMG_COL_WIDTH)
    worksheet.set_row(0, 24)
    worksheet.freeze_panes(1, 0)

    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})
    cache = {}

    for i, c in enumerate(comments, start=1):
        worksheet.set_row(i, ROW_HEIGHT_PT)
        worksheet.write(i, 0, c["author"], cell)
        worksheet.write(i, 1, c["content"], wrap)
        worksheet.write(i, 2, c["likes"], center)
        worksheet.write(i, 3, "", center)  # 이미지 자리(테두리용 빈 셀)

        thumb = fetch_thumbnail(session, c["profile"], cache)
        if thumb:
            buffer, width = thumb
            scale = IMG_BOX_PX / width
            worksheet.insert_image(
                i, 3, "profile.png",
                {
                    "image_data": BytesIO(buffer.getvalue()),
                    "x_scale": scale,
                    "y_scale": scale,
                    "x_offset": 8,
                    "y_offset": 2,
                    "object_position": 1,  # 셀 크기에 따라 같이 움직이고 늘어남
                },
            )
        elif c["profile"]:
            worksheet.write(i, 3, c["profile"], center)

    # 마지막 줄에 어떤 영상인지 남겨둔다.
    worksheet.write(len(comments) + 2, 0, f"영상 : {video_title}")
    workbook.close()


# ---------------------------------------------------------------- 실행

def main():
    parser = argparse.ArgumentParser(description="유튜브 댓글 크롤러")
    parser.add_argument("url", nargs="?", default=DEFAULT_URL, help="유튜브 영상 URL")
    parser.add_argument("--max", type=int, default=100,
                        help="가져올 최대 댓글 수 (0이면 끝까지, 기본 100)")
    parser.add_argument("--show", action="store_true", help="브라우저 창을 띄운다")
    parser.add_argument("--out", default=str(SAVE_PATH), help="저장할 엑셀 경로")
    args = parser.parse_args()

    title, comments = crawl(args.url, args.max, headless=not args.show)

    if not comments:
        print("수집된 댓글이 없습니다.")
        return 1

    save_path = Path(args.out)
    save_excel(comments, save_path, title)
    print(f"댓글 {len(comments)}개 저장 완료 -> {save_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
