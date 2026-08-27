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

# 아마존 캔들스틱 느낌 - 고가/저가/종가 밴드
plt.figure(figsize=(14,6))
plt.fill_between(df_amz.index, df_amz['Low'], df_amz['High'], alpha=0.2, color = 'orange')
plt.plot(df_amz.index, df_amz['Close'], label='Amazon (AMZN)', color = 'orange')
plt.plot(df_goog.index, df_goog['Close'], label='Google (GOOG)', color = 'blue')
plt.title('Amazon (AMZN) 주가 변동 범위')
plt.xlabel('날짜')
plt.ylabel('종가 (USD)')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig( BASE_DIR/'amz_price_range.png', dpi=150)
plt.show()



# 3) 거래량 비교 (막대그래프)
# sharex -> x축 쉐어 (해당 코드에서는 날짜를 공유함.)
fig, axes = plt.subplots(2,1,figsize=(14,8), sharex=True)
# bar = 막대그래프
axes[0].bar(df_amz.index, df_amz['Volume'], color='orange', width=1)
axes[0].set_title('Amazon 거래량')
axes[0].set_ylabel('거래량')

axes[1].bar(df_goog.index, df_goog['Volume'], color='blue', width=1)
axes[1].set_title('Google 거래량')
axes[1].set_ylabel('거래량')
axes[1].set_xlabel('날짜')

plt.tight_layout()
plt.savefig( BASE_DIR/'amz_goog_volume.png', dpi=150)
plt.show()


# 4) 수익률(%) 비교 - 시작일 대비 등락률

amz_return = (df_amz['Close']/df_amz['Close'].iloc[0]-1)*100
goog_return = (df_goog['Close']/df_goog['Close'].iloc[0]-1)*100

plt.figure(figsize=(14,6))

plt.plot(df_amz.index, amz_return, label='Amazon (AMZN)', color = 'orange')
plt.plot(df_goog.index, goog_return, label='Google (GOOG)', color = 'blue')
plt.axhline(0, color='gray', linestyle = '--', linewidth=1)
plt.title('아마존 vs 구글 누적 수익률 비교 (시작일 대비 %)')
plt.xlabel('날짜')
plt.ylabel('수익률 (%)')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig( BASE_DIR/'amz_goog_return_compare.png', dpi=150)
plt.show()

print("\n시각화 완료 - 이미지 4개 저장됨")