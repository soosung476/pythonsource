import requests
import json
from pathlib import Path
from dotenv import load_dotenv
import os

BASE_DIR = Path(__file__).resolve().parent

load_dotenv()
API_KEY = os.getenv("TMDB_API_KEY")


BASE_URL = "https://api.themoviedb.org/3"
IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"

# 영화 상세 정보
def get_popular_movie(count=10):
    url = f"{BASE_URL}/movie/popular"
    params = {
        "api_key":API_KEY,
        "language":"ko-KR",
        "page":1
    }
    res = requests.get(url, params=params)
    res.raise_for_status()
    data = res.json()

    return data['results'][:count] # 인기순으로 이미 정렬되어 옴

def get_movie_detail(movie_id):
    url = f"{BASE_URL}/movie/{movie_id}"
    params = {
        "api_key":API_KEY,
        "language":"ko-KR"
    }
    res = requests.get(url, params=params)
    res.raise_for_status()
    return res.json()


def main():
    popular_movies = get_popular_movie(10)

    print("=== 현재 인기 영화 TOP 10 ===\n")
    results = []

    for i, movie in enumerate(popular_movies, start=1):
        detail = get_movie_detail(movie['id']) # 영화 아이디로 상세 정보 가져오기

        info = {
            "순위":i,
            "제목":detail['title'],
            "개봉일":detail['release_date'],
            "평점":detail['vote_average'],
            "러닝타임":f"{detail['runtime']}분",
            "줄거리":detail['overview'][:80] + "..." if len(detail['overview'])>80 else detail['overview'],
            "포스터":IMAGE_BASE_URL+detail['poster_path'] if detail['poster_path'] else None
        }

        print(f"{i}위 | {info['제목']} | 평점 {info['평점']} | 개봉 {info['개봉일']}")
        results.append(info)
    json_path = BASE_DIR/"popular_movie_top10.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print("\n저장 완료: popular_movie_top10.json")

if __name__=="__main__":
    main()
