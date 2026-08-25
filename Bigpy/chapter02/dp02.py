import pandas as pd
import numpy as np
import openpyxl
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR.parent / "data"


df1 = pd.DataFrame(np.random.randint(0,100, size=(100,4)), columns=['ONE','TWO','THREE','FOUR'])
print(df1)

# 평균 0이고 표준편차가 1인 정규분포 실수 생성 (10행 2열 컬럼명 AB)
df2 = pd.DataFrame(np.random.randn(10,2), columns=list('AB'))
print(df2)

df1.to_csv(DATA_DIR/"result2.csv", index=False)
df2.to_excel(DATA_DIR/"result2.xlsx",header=True ,index=None)