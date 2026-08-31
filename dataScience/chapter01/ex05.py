# -*- coding: utf-8 -*-

import pandas as pd

"""
- sort_values()로 오름차순/내림차순 정렬
- 여러 기준으로 동시에 정렬(정렬 우선순위)
- rank()로 순위 컬럼을 직접 만들기
- ascending = True(오름차순, 기본값)/False(내림차순) 옵션
"""

df = pd.read_csv("../data/webtoon_ranking.csv", encoding="utf-8-sig")
print("=== 원본데이터 ===")
print(df)

# 1. 조회수 기준 내림차순 정렬(1위부터)
by_views = df.sort_values("조회수", ascending=False)
print("\n === 조회수 순위 === ")
print(by_views[["웹툰제목","조회수"]])

# 2. 별점 기준 오름차순 정렬 (낮은 평점부터, ascending = True인데 생략 가능)
by_rating_asc = df.sort_values("별점")
print("\n === 별점 순위 ===")
print(by_rating_asc[["웹툰제목","별점"]])

# 3. 여러 기준을 정렬 : 장르별로 묶고, 그 안에서 조회수 내림차순
by_genre_views = df.sort_values(["장르", "조회수"], ascending=[True,False])
print("\n === 장르별 -> 조회수 내림차순 ===")
print(by_genre_views[["장르","웹툰제목","조회수"]])

# 4. rank(): 순위를 숫자로 매겨서 새 컬럼으로 저장
df["조회수순위"] = df["조회수"].rank(ascending=False).astype(int)
print("\n === 순위 컬럼 추가 ===")
print(df[["웹툰제목","조회수","조회수순위"]].sort_values("조회수순위", ascending=True))


# 5. nlargest / nsmllest : 상위/하위 n개만 빠르게 뽑기
print("\n === 조회수 TOP3 (nlargest) ===")
print(df.nlargest(3,"조회수")[["웹툰제목","조회수"]])

