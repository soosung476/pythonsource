import requests
from bs4 import BeautifulSoup

url = "http://books.toscrape.com/"

res = requests.get(url)
res.encoding = 'utf-8'
soup =BeautifulSoup(res.text, 'html.parser')

books = soup.select("article.product_pod")
for book in books:
    title =book.select_one("h3 > a")['title']
    price = book.select_one("p.price_color").text
    rating = book.select_one("p.star-rating")["class"][1]

    print(f"{title} | {price} | 별점 {rating}")