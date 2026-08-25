import sys
import io
from bs4 import BeautifulSoup   # pip install beautifulsoup4


html = '''
<html>
<body>
  <h1>Find vs Select 차이</h1>
  <p>css 선택자를 사용 및 다중반환</p>
  <p>태그선택자 사용 및 단일반환</p>
</body>
</html>
'''

# print('html -> ',html)
# print("*"*40)
soup = BeautifulSoup(html, 'html.parser')

# print('soup -> ',type(soup))
# print(soup)

# print("*"*40)
print('prettify', soup.prettify())

####################################################

h1 = soup.html.body.h1
print("h1 -> ",h1)

p1 = soup.html.body.p
print("h1 -> ",p1)

p2 = p1.next_sibling.next_sibling # p태그의 경우 줄바꿈 할 때 공백이 추가돼서, next_sibling시 공백이 나옴, 두 번 해줘야 됨.
print("p2 -> ",p2)

p3 = p1.previous_sibling.previous_sibling # 위로 올라갈 때도, 공백이 있으므로 두 번 해줘야 한다, 즉 <태그> 공백 <p>태그 이기 때문에 p태그에서 sibling을 할 때 조심.
print("p3 -> ", p3)

