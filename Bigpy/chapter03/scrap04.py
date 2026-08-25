import sys
import io
from bs4 import BeautifulSoup   # pip install beautifulsoup4
from urllib.parse import urljoin



html = """
<html><body>
  <ul>
    <li><a href="http://www.naver.com">naver</a></li>
    <li><a href="http://www.daum.net">daum</a></li>
    <li><a href="https://www.google.com">google</a></li>
    <li><a href="https://www.tistory.com">tistory</a></li>
  </ul>
</body></html>
"""

soup = BeautifulSoup(html, 'html.parser')
print('prettify', soup.prettify())


# <a> 태그중에서 찾기

a = soup.find_all("a", string="daum") # select
b = soup.find_all("a", string=["naver","daum"]) 
c = soup.find_all("a",limit=2)
d = soup.find("a") # select_one

print(a)
print(b)
print(c)
print(d)

print("-"*40)
links = soup.find_all("a")
print('links -> ',links)

for a in links:
    href=a.attrs['href']
    print('href -> ',href)
    text = a.string
    print('text -> ',text)

baseUrl = "http://test.com/html/a.html"
print(urljoin(baseUrl,"../sub/c.html")) # "http://test.com/sub/c.html"
print(urljoin(baseUrl,"../index.html")) # "http://test.com/index.html"
print(urljoin(baseUrl,"../img/ho.png")) # "http://test.com/img/ho.png"
print(urljoin(baseUrl,"../c.html")) # "http://test.com/css/ho.css"