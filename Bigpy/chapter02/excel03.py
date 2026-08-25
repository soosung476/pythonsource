import pandas as pd
import numpy as np
import openpyxl
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR.parent / "data"


df= pd.read_excel(DATA_DIR/'excel_s1.xlsx', sheet_name=0, engine='openpyxl')
# print(df.head()) # 상위 5개 뽑아옴
# print(df.tail()) # 하위 5개 뽑아옴
# print(df)
df= pd.read_excel(DATA_DIR/'excel_s1.xlsx', sheet_name=0, skiprows=[1])
# print(df.head())

df= pd.read_excel(DATA_DIR/'excel_s1.xlsx', sheet_name=0, skiprows=[1], skipfooter=5)
# print(df.tail())

df= pd.read_excel(DATA_DIR/'excel_s1.xlsx', header=0)
# print(df.head())
# print(list(df))
print(list(df.columns.values))

# 전처리
# ^Unnamed : Unnamed로 시작하는 열
df= df.loc[:,~df.columns.str.contains('^Unnamed')] # 정규화
# na_values = '...' => null

df= pd.read_excel(DATA_DIR/'excel_s1.xlsx', header=0, na_values='...', converters={"2019": lambda w:w if w>60000 else None})
print(df.head())