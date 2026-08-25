import pandas as pd
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR.parent / "data"
file_path = DATA_DIR/"csv_s1.csv"
csv2_path = DATA_DIR/"csv_s2.csv"

df = pd.read_csv(file_path)
# print(df)

# 0번째 행 스킵
df = pd.read_csv(file_path, skiprows=[0])
# print(df)

# 0번째 행 스킵 header 생략
df = pd.read_csv(file_path, skiprows=[0], header=None)
# print(df)

# 0번째 행 스킵 header 생략, 헤더네임 지정
df = pd.read_csv(file_path, skiprows=[0], header=None, names=["Month", 2023,2024,2025])
# print(df)

# 0번째 행 스킵 header 생략, 인덱스 지정 row의 이름이 0,1,2,3 대신 0번컬럼에 있는 것으로 대체.
df = pd.read_csv(file_path, skiprows=[0], header=None, names=["Month", 2023,2024,2025], index_col=[0])
# print(df)

df2 = pd.read_csv(csv2_path, sep=';', skiprows=[0], \
                 header=None, names=["First name", "Test1", "Test2", "Test3", "Final", "Grade"])
print(df2)

df2['Sum'] = df2[['Test1','Test2','Test3','Final']].sum(axis=1)
print(df2)

df2['Avg'] = df2[['Test1','Test2','Test3','Final']].mean(axis=1)
print(df2)

df2.to_csv(DATA_DIR/"result.csv", index=False)