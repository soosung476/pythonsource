import sys
import io
from bs4 import BeautifulSoup   # pip install beautifulsoup4



html = """
<html><body>
<div id="main">
  <h1>강의목록</h1>
  <ul class="lecs">
    <li>Java 최고수 되기</li>
    <li>파이썬 기초 프로그래밍</li>
    <li>파이썬 머신러닝 프로그래밍</li>
    <li>안드로이드 블루투스 프로그래밍</li>
  </ul>
</div>
</body></html>
"""

soup = BeautifulSoup(html, 'html.parser')
# print('prettify ',soup.prettify())

h1 = soup.select_one("#main > h1").string
# print('h1: ', h1)

li_list=soup.select("div#main > ul.lecs > li")
print('li_list: ', li_list)

for li in li_list:
    print('li -> ',li)
    print('li -> ',li.string)