import pandas as pd
import numpy as np
import openpyxl
from pathlib import Path
import sys
import os
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR.parent / "data"

df1= pd.read_excel(DATA_DIR/'excel_s1.xlsx', header=0)
# print(df1)

df1['State']=df1['State'].str.replace(' ', '|')
# print(df1['State'])
# 평균 컬럼 추가
df1['Avg']=df1[['2018','2019','2020']].mean(axis=1).round(2)
# print(df1)
# 합계 컬럼 추가
df1['Sum']=df1[['2018','2019','2020']].sum(axis=1)
# print(df1)
# 최대값 컬럼 추가
df1['Max']=df1[['2018','2019','2020']].max(axis=1)
# print(df1)

# 최대값 열단위
max_values=df1[['2018','2019','2020']].max(axis=0)
# print(max_values)

# 최소값 열단위
min_values=df1[['2018','2019','2020']].min(axis=0)
# print(min_values)


# 상세 분석 정보
# print(df1.describe())

# 엑셀쓰기
# df1.to_excel(DATA_DIR/"result_s1.xlsx", index=False)

# 컬럼 연산 추가
df2= pd.read_excel(DATA_DIR/'excel_s2.xlsx', header=0)
df2[['Units','UnitCost']] = df2[['Units','UnitCost']].astype(int)
df2['Custom1']= df2['Units']*df2['UnitCost']
df2['Custom2']= df2['Total']*10
print(df2)

df2.to_excel(DATA_DIR/"result_s22.xlsx", index=False)
print("완료")