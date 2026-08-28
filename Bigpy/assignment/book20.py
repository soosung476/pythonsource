import requests
import csv
from bs4 import BeautifulSoup

from pathlib import Path

BASE_PATH = Path(__file__).resolve().parent

url = "https://books.toscrape.com/"

res = requests.get(url)
res.encoding = 'utf-8'
soup = BeautifulSoup(res.text, 'html.parser')

data_list = soup.select(".product_pod")[:20]
print(data_list)

results = []
for i, data in enumerate(data_list, start=1):
    title_tag = data.select_one("h3 a")
    title = title_tag['title']
    # print(title)
    price_tag = data.select_one("div.product_price > .price_color")
    price = price_tag.text
    # print(price)
    star_tag = data.select_one("p")
    star = star_tag['class'][1]
    # print(star)
    print(f"{i}. {title} | {price} | 별점: {star}")

    results.append({"순번":i ,
                    "제목":title,
                    "가격":price,
                    "별점":star})
    
    
csv_path = BASE_PATH/"book_top20.csv"
with open(csv_path,'w', newline="", encoding='utf-8-sig') as f:
    writer = csv.DictWriter(f, fieldnames=["순번","제목","가격","별점"])
    writer.writeheader()
    writer.writerows(results)
    print("저장 완료: book_top20.csv")