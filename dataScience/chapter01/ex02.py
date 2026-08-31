# -*- coding: utf-8 -*-

"""
- read_csv()로 실제 파일을 불러오기
- 컬럼명, 데이터 타ㅣㅂ을 확인
- 인코딩 문제(한글 깨짐)에 대비
- 한글 CSV는 encoding="utf-8-sig"또는 "cp949"로 열어야 하는 경우가 많음
    (Excel에서 저장한 CSV는 보통 cp949/euc-kr인 경우가 많음)
- dtypes로 컬럼별 자료형을 확인하는 습관을 들이면 이후 groupby/apply에서 삽질 감소
"""

import pandas as pd

# 1. CSV파일 불러오기
df = pd.read_csv("../data/convenience_sales.csv", encoding="utf-8-sig")
# print(df)
# print(type(df))

# 2. 컬럼명 확인
print("=== columns list ===")
print(df.columns.to_list())

# 3. 데이터 타입 확인
print('\n=== 데이터 타입(dtype) ===')
print(df.dtypes)

# 4. shape: 행 개수, 열 개수
print(f"\n=== shape: {df.shape} (행{df.shape[0]} 개, 열{df.shape[1]} 개) ===")

# 5. 상위 5개
print("\n === head() ===")
print(df.head(5))

# 6. 특정 컬럼만 보기
print("\n === 상품명; 판매수량만 각각 5개 보기 ===")
print(df[['상품명','판매수량']].head(5))

# 7. 매출액(판매수량 * 단가) 컬럼 새로 추가
print("\n === 매출액 컬럼 추가 후 ===")
df["매출액"] = df['판매수량']*df['단가']
print(df.head())