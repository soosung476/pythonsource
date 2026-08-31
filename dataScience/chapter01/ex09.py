# -*- coding: utf-8 -*-

import pandas as pd

"""
- 두 개의 DataFrame을 공통 키(학번) 기준으로 합치는(merge) 방법
- how 옵션(inner/left/right/outer)의 차이
- SQL의 JOIN과 완전히 같은 개념
- "학생정보엔 있는데 성적표엔 없는 학생이 있다면?" 같은 상황을 만들어서
  how 옵션별로 결과가 어떻게 달라지는지 직접 비교
"""

student_info = pd.read_csv("../data/student_info.csv", encoding="utf-8-sig")
student_scores = pd.read_csv("../data/student_scores.csv", encoding="utf-8-sig")

print("=== 학생 정보 ===")
print(student_info)
print("\n=== 성적표 ===")
print(student_scores)

# 1. 기본 merge
merged = pd.merge(student_info, student_scores, on="학번")
print("\n === merge 결과 (inner, 기본값) ===")
print(merged)

# 2. 성적표에 없는 학생을 일부러 만들어서 how 옵션 비교
student_info_extra = pd.concat([student_info, pd.DataFrame({"학번":[1007], "이름":["오세훈"],"반":["3반"]})
                               ],ignore_index=True)

print("\n=== 성적표에 없는 학생(1007) 추가된 학생정보 ===")
print(student_info_extra)

# 3. how = "left": 왼쪽(student_info_extra) 기준으로 전부 유지, 없는 성적은 NaN
left_merged = pd.merge(student_info_extra, student_scores, on="학번", how="left")
print("\n=== how = 'left'의 결과 없는 학생(1007) 성적은 NaN ===")
print(left_merged)

# 4. how = "inner": 양쪽에 모두 존재하는 학번만 남김
inner_merged = pd.merge(student_info_extra, student_scores, on="학번", how="inner")
print(f"\n=== how = 'inner'의 결과 {len(inner_merged)}명만 남음 (1007번 제외) ===")
print(inner_merged)

# 5. 합친 데이터로 반별 평균 국어 점수 확인
avg_korean = merged.groupby("반")["국어"].mean()
print("\n === merge 후 반별 국어 평균 ===")
print(avg_korean)

# 성적표 : 키 컬럼명이 다를 경우
score_table = pd.DataFrame({
    "학생번호": [1001, 1002, 1003, 1005], 
    "국어": [85, 90, 78, 92],
    "영어": [88, 76, 95, 80],
})

print("\n === 학생 정보(키: 학생번호) ===")
print(score_table)

# 6 컬럼명이 다를 경우 merge
merged2 = pd.merge(student_info, score_table, left_on="학번", right_on="학생번호", how= "inner")
print("\n === 컬럼명이 다른 테이블의 merge 결과 (inner) ===")
print(merged2)