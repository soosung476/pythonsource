from bs4 import BeautifulSoup
import requests

# 주식 요청 url
url = "https://finance.naver.com/sise/"

headers={
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/151.0.0.0 Safari/537.36"
}

res = requests.get(url, headers=headers)
# 인코딩 알아내는 법
# print(res.encoding)
res.encoding = "euc-kr"
soup = BeautifulSoup(res.text, "html.parser")

table = soup.select_one(f"#siselist_tab_0")
print(f'오늘의 최고 상한가 종목')
ranking = table.select("a.tltle")[:10]
for rank, stock in enumerate(ranking, start=1):
    print(f"{rank}위 {stock.text}")
print("-" * 45)