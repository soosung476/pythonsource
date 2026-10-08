"""Google Fonts에서 영상에 쓰는 한글 폰트(OFL)를 내려받는다.

    python3 fetch_fonts.py

fonts/ 폴더에 TTF 파일이 저장된다 (저장소에는 커밋하지 않음).
"""
import http.client
import re
import sys
import time
import urllib.request
from pathlib import Path

FONT_DIR = Path(__file__).resolve().parent / "fonts"

# (Google Fonts family 쿼리, 저장 파일 이름 접두사)
FAMILIES = [
    ("Noto+Serif+KR:wght@400;700;900", "NotoSerifKR"),
    ("Noto+Sans+KR:wght@300;500;700;900", "NotoSansKR"),
    ("Song+Myung", "SongMyung"),
    ("Hahmlet:wght@300;700;900", "Hahmlet"),
    ("Nanum+Myeongjo:wght@400;700;800", "NanumMyeongjo"),
    ("Gowun+Batang:wght@400;700", "GowunBatang"),
    ("Black+Han+Sans", "BlackHanSans"),
]

BLOCK = re.compile(r"font-weight:\s*(\d+);.*?src:\s*url\((\S+?)\)", re.S)


def fetch(url: str, tries: int = 5) -> bytes:
    # 브라우저 UA를 보내지 않으면 Google Fonts가 분할되지 않은 TTF 한 벌을 돌려준다.
    req = urllib.request.Request(url, headers={"User-Agent": "curl/8"})
    for attempt in range(tries):
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                return resp.read()
        except (http.client.IncompleteRead, ConnectionError, TimeoutError):
            if attempt == tries - 1:
                raise
            time.sleep(2 ** (attempt + 1))
    raise AssertionError("unreachable")


def main() -> int:
    FONT_DIR.mkdir(exist_ok=True)
    for query, prefix in FAMILIES:
        css = fetch(f"https://fonts.googleapis.com/css2?family={query}").decode()
        for weight, url in BLOCK.findall(css):
            out = FONT_DIR / f"{prefix}-{weight}.ttf"
            if out.exists():
                continue
            out.write_bytes(fetch(url))
            print(f"{out.name}: {out.stat().st_size / 1e6:.1f} MB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
