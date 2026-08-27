import datetime
import FinanceDataReader as fdr

import matplotlib.pyplot as plt
import matplotlib as mpl
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


mpl.rcParams['font.family'] = 'AppleGothic'
mpl.rcParams['axes.unicode_minus'] = False


start = datetime.datetime(2023,2,19)

end = datetime.date(2024,7,30)

# 구글: google finanace = https://www.google.com/finance/?h1=ko
# 한국거래소 상장종목 전체

df_krx = fdr.StockListing('KRX')

# 리스트 10개 출력
print(df_krx.head(10))

print(df_krx.index)
print(df_krx['Stocks'])
print(df_krx.iloc[0]) # 첫 번째 종목
print(df_krx.describe()) 

print("-"*100)
# 미국거래소 상장종목 중 아마존 금융정보

df_amz = fdr.DataReader('AMZN', start, end)
print(df_amz.head(10))
print(df_amz.iloc[0]) 
print(df_amz.loc['2024-07-16']) # 첫 번째 종목
print(df_amz.describe()) 

print("-"*100)
# 미국거래소 상장종목 중 구글 금융정보
df_goog = fdr.DataReader('GOOG', start, end)
print(df_goog.head(10))
print(df_goog.iloc[0]) 
print(df_goog.loc['2024-07-16']) # 첫 번째 종목
print(df_goog.describe()) 

plt.figure(figsize=(14,6))
plt.plot(df_amz.index, df_amz['Close'], label='Amazon (AMZN)', color = 'orange')
plt.plot(df_goog.index, df_goog['Close'], label='Google (GOOG)', color = 'blue')
plt.title('아마존 vs 구글 종가 추이 (2023.02 ~ 2024.07)')
plt.xlabel('날짜')
plt.ylabel('종가 (USD)')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig( BASE_DIR/'amz_goog_close_compare.png', dpi=150)
plt.show()