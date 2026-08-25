import requests
from bs4 import BeautifulSoup


url = "http://books.toscrape.com/"

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/151.0.0.0 Safari/537.36"
}

res = requests.get(url, headers=headers)
soup =BeautifulSoup(res.text, 'html.parser')

# print(soup)

book = soup.find("article", class_ = "product_pod")
print("제목: ",book.find("h3").find("a")['title'])
print("가격: ",book.find("p", class_="price_color").text.strip())

# print(book)