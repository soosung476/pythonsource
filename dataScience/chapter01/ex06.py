# -*- coding: utf-8 -*-

import pandas as pd


"""
- 결측치(NaN)을 찾고(isnull), 채우고(fillna), 제거하는(dropna) 3가지 방법을 익힌다.
- 출석부의 빈칸(NaN)이 실제로는 '기록 누락'인지 '결석'인지 상황에 따르게 다르게 처리해야 함.
- fillna()는 값을 채우는 것, dropna()는 행/열 자체를 지우는 것 -> 목적이 다름.
"""

df = pd.read_csv("../data/attendance.csv", encoding="utf-8-sig")
print("=== 원본 출석부 (NaN = 기록누락) ===")
print(df)

# 1. isnull(): 결측치값인지 아닌지
print("\n=== isnull(): rufcmrcl duqn ===")
print(df.isnull())

# 2. 컬럼별 결측치 개수 세기
print("\n === 컬럼별 결측치 개수 ===")
print(df.isnull().sum())

# 3. 결측치가 하나라도 있는 행만 뽑아보기
rows_with_na = df[df.isnull().any(axis=1)]
print(f"\n === 결측치가 하나라도 있는 학생의 수 ({len(rows_with_na)} 명) ===")

# 4. fillna(): 결측치를 특정 값으로 채우기
df_filled= df.fillna("결석")
print(f"\n === fillna('결석')으로 채운 결과 ===")
print(df_filled)

# 5. dropna() : 결측치가 있는 행을 통째로 제거
df_dropped = df.dropna()
print(f"\n === dropna() 결과 {len(df)}명 -> {len(df_dropped)}명으로 감소 ===")
print(df_dropped)