# -*- coding: utf-8 -*-

import pandas as pd
"""
- apply()로 컬럼의 각 값에 함수를 적용해 새 컬럼 생성
- lambda(익명 함수)와 일반 함수(def) 두 가지 방식 적용
- apply는 "각 값을 하나씩 꺼내서 함수에 넣고, 결과를 다시 컬럼으로 모은다"
  엑셀의 IF 함수와 비슷
- 조건이 복잡해지면 lambda보다 일반 함수(def)가 가독성이 좋음.
"""

df = pd.read_csv("../data/allowance.csv", encoding="utf-8-sig")
print("=== 원본 용돈 데이터 ===")
print(df)

# 1. 일반 함수로 등급 매기는 로직
def get_grade(amount):
    if amount < 20000:
        return "짠돌이"
    elif amount <70000:
        return "보통"
    else :
        return "부자"
    
# 2. apply(): 함수를 컬럼 전체에 적용해서 새 컬럼 생성
df["등급"] = df["월용돈"].apply(get_grade)
print("\n === 일반 함수로 등급 매긴 결과 ===")
print(df)

# 3. lambda로 활용
df["짠돌이여부"] = df["월용돈"].apply(lambda x: "짠돌이" if x<20000 else "짠돌이아님")
print("\n lambda로 간단 조건 처리")
print(df)
print(df[["이름","월용돈","짠돌이여부"]])

# 4. 여러 컬럼을 동시에 참조해야 할 때 axis = 1
df["연간환산"] = df.apply(lambda row: row["월용돈"]*12, axis=1)
print("\n lambda로 행전체를 활용할 때")
print(df)
print(df[["이름","월용돈","연간환산"]])

# 5. 등급별 인원수 확인, 부자 등급만 정렬해서 출력
print(f"\n=== 등급별 인원수 groupby ===")
print(df["등급"].value_counts())

rich_students = df[df["등급"]=="부자"].sort_values("월용돈", ascending=False)
print("\n=== '부자' 등급 학생(용돈이 많은 순서) ===")
print(rich_students[["이름","월용돈"]])