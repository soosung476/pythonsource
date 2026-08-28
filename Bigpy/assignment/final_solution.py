"""
문제 5 (난이도 상) — 종합: API + 동적크롤링 + 엑셀(이미지 포함) 저장 + 자동화
1) TMDB API로 인기 영화 TOP 5 (제목/평점/개봉일/포스터) 조회
2) Playwright로 각 영화 제목을 네이버에 검색해서 노출되는 평점/리뷰 정보 크롤링
3) 두 결과를 영화 제목 기준으로 합쳐서 엑셀(xlsx)로 저장 (포스터 이미지 삽입)
4) 파일 맨 아래에 배치파일 + 작업 스케줄러 등록 방법 주석으로 안내

사전 준비:
1. TMDB에서 API 키 발급 → .env에 TMDB_API_KEY=... 저장
2. 설치: uv pip install python-dotenv requests playwright xlsxwriter beautifulsoup4
3. playwright install chromium (최초 1회)
"""

import requests
import os
import time
from io import BytesIO
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import xlsxwriter
import urllib.request as req
from urllib.parse import quote_plus

from pathlib import Path
Py_Scrap = Path(__file__).resolve().parent.parent/"Py_Scrap"

load_dotenv()
TMDB_API_KEY = os.getenv("TMDB_API_KEY")

TMDB_BASE_URL = "https://api.themoviedb.org/3"
IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"


def get_popular_movies(count=5):
    url = f"{TMDB_BASE_URL}/movie/popular"
    params = {
        "api_key": TMDB_API_KEY,
        "language": "ko-KR",
        "page": 1
    }
    res = requests.get(url, params=params)
    res.raise_for_status()
    data = res.json()

    return data["results"][:count]


def get_movie_detail(movie_id):
    url = f"{TMDB_BASE_URL}/movie/{movie_id}"
    params = {
        "api_key": TMDB_API_KEY,
        "language": "ko-KR"
    }
    res = requests.get(url, params=params)
    res.raise_for_status()
    return res.json()


def fetch_tmdb_top5():
    popular = get_popular_movies(5)
    movies = []

    for i, m in enumerate(popular, 1):
        detail = get_movie_detail(m["id"])

        poster_url = (
            IMAGE_BASE_URL + detail["poster_path"]
            if detail.get("poster_path") else None
        )

        movies.append({
            "순위": i,
            "제목": detail["title"],
            "TMDB평점": detail["vote_average"],
            "개봉일": detail["release_date"],
            "포스터": poster_url
        })

        time.sleep(0.2)

    return movies


def search_naver_movie_info(page, title):
    try:
        search_query = f"{title} 영화 평점"
        search_url = f"https://search.naver.com/search.naver?query={quote_plus(search_query)}"

        page.goto(search_url)
        page.wait_for_timeout(2000)

        score_locator = page.locator("span.cm_icon_star")

        if score_locator.count() > 0:
            parent_text = score_locator.first.locator("xpath=..").inner_text()
            return parent_text.strip()
        else:
            return "정보없음"

    except Exception as e:
        print(f"'{title}' 네이버 평점 조회 실패: {e}")
        return "정보없음"


def fetch_naver_scores(movie_titles):
    results = {}

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page(viewport={"width": 1280, "height": 900})

        for title in movie_titles:
            score = search_naver_movie_info(page, title)
            print(f"[네이버 검색] {title} → {score}")
            results[title] = score
            page.wait_for_timeout(500)

        browser.close()

    return results


def merge_results(tmdb_movies, naver_scores):
    for movie in tmdb_movies:
        movie["네이버평점"] = naver_scores.get(movie["제목"], "정보없음")
    return tmdb_movies


def save_to_excel(movies, filename=Py_Scrap/"data/movie_report.xlsx"):
    workbook = xlsxwriter.Workbook(filename)
    worksheet = workbook.add_worksheet()

    headers = ["순위", "제목", "TMDB평점", "개봉일", "네이버평점", "포스터"]
    for col, h in enumerate(headers):
        worksheet.write(0, col, h)

    row = 1
    for movie in movies:
        worksheet.write(row, 0, movie["순위"])
        worksheet.write(row, 1, movie["제목"])
        worksheet.write(row, 2, movie["TMDB평점"])
        worksheet.write(row, 3, movie["개봉일"])
        worksheet.write(row, 4, movie["네이버평점"])

        poster_url = movie.get("포스터")
        if poster_url:
            try:
                request = req.Request(poster_url, headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
                })
                img_data = BytesIO(req.urlopen(request, timeout=10).read())

                worksheet.insert_image(
                    row, 5, movie["제목"],
                    {"image_data": img_data, "x_scale": 0.3, "y_scale": 0.3}
                )
                worksheet.set_row(row, 100)
            except Exception as e:
                print(f"포스터 다운로드 실패 ({movie['제목']}): {e}")
                worksheet.write(row, 5, poster_url)
        else:
            worksheet.write(row, 5, "포스터없음")

        row += 1

    workbook.close()
    print(f"\n엑셀 저장 완료: {filename}")


def main():
    print("=== 1단계: TMDB 인기 영화 TOP 5 조회 ===")
    tmdb_movies = fetch_tmdb_top5()
    for m in tmdb_movies:
        print(f"{m['순위']}위 | {m['제목']} | TMDB평점 {m['TMDB평점']} | 개봉 {m['개봉일']}")

    titles = [m["제목"] for m in tmdb_movies]

    print("\n=== 2단계: 네이버 검색으로 평점 추가 조회 ===")
    naver_scores = fetch_naver_scores(titles)

    print("\n=== 3단계: 결과 병합 ===")
    merged = merge_results(tmdb_movies, naver_scores)
    for m in merged:
        print(m)

    print("\n=== 4단계: 엑셀 저장 ===")
    save_to_excel(merged)


if __name__ == "__main__":
    main()