# -*- coding: utf-8 -*-
"""
- duplicated()로 중복 행을 찾아냄
- drop_duplicates()의 subset, keep 옵션을 활용
- "전체 행이 완전히 같아야 중보"인지, "특정 컬럼(응답자ID)만 같아도 중복"인지
  기준을 명확히 정해야 함 -> subset 옵션이 핵심.
- keep="fist"(기본값)/"last"/False 차이
"""
import pandas as pd

df = pd.read_csv("../data/survey.csv", encoding="utf-8-sig")
print(f"=== 원본 설문 응답 ({len(df)}건) ===")
print(df)

# 1. duplicated(): 응답자ID 기준으로 중복 여부 확인
print("\n === 응답자ID 기준으로 중복 여부 확인 ===")
print(df.duplicated(subset="응답자ID"))

# 2. 중복된 응답자ID만 골라서 전체(keep=False)출력
dup_rows = df[df.duplicated(subset="응답자ID", keep=False)]
print(dup_rows.sort_values("응답자ID"))

# 3. drop_duplicates(): 중복 제거, 기본은 첫 번째 응답만 유지(keep = "first")
df_first = df.drop_duplicates(subset="응답자ID", keep="first")
print(f"\n === keep='first' 결과: ({len(df)})건 -> ({len(df_first)})건 ===")

# 4. keep="last" 마지막 응답만 유지
df_last = df.drop_duplicates(subset="응답자ID", keep="last")
print(f"\n === keep='last' 결과: ({len(df)})건 -> ({len(df_last)})건 ===")

# 5. keep="False": 중복된 데이터 전체 제거
df_unique_only = df.drop_duplicates(subset="응답자ID", keep=False)
print(f"\n === keep=False 결과: ({len(df)})건 -> ({len(df_unique_only)})건 (중복자 모두 제외)===")